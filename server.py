#!/usr/bin/env python3
import socket

def receive_http_request(client_socket):
    """
    Receives HTTP request data with proper handling of Content-Length
    """
    data = []
    content_length = None
    headers_complete = False
    
    while True:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        
        data.append(chunk)
        raw_data = b''.join(data)
        
        # If we haven't found the end of headers yet, look for it
        if not headers_complete and b'\r\n\r\n' in raw_data:
            headers_complete = True
            headers = raw_data.split(b'\r\n\r\n')[0].decode('utf-8', errors='ignore')
            
            # Look for Content-Length header
            for line in headers.split('\r\n'):
                if line.lower().startswith('content-length:'):
                    content_length = int(line.split(':', 1)[1].strip())
                    break
        
        # If we have all headers and know the content length
        if headers_complete and content_length is not None:
            if len(raw_data) >= raw_data.find(b'\r\n\r\n') + 4 + content_length:
                break
        
        # If we have headers but no content length, assume we're done
        elif headers_complete:
            break
    
    if data:
        return raw_data.decode('utf-8', errors='ignore')
    return None

def parse_http_request(request_data):
    """
    Extracts the actual request body from HTTP request
    """
    try:
        # Split headers and body
        if '\r\n\r\n' in request_data:
            headers, body = request_data.split('\r\n\r\n', 1)
            
            # For POST requests, return the body
            if 'POST' in request_data.split('\n')[0]:
                return body.strip()
            
            # For other requests, return the first line (usually the request line)
            return request_data.split('\n')[0].strip()
        else:
            return request_data.strip()
    except Exception as e:
        print(f"Error parsing request: {e}")
        return request_data.strip()

def create_http_response(content):
    """
    Creates a valid HTTP response with the provided content
    """
    html_content = f"<html>{content}</html>"
    response = f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: {len(html_content)}

{html_content}"""
    return response.encode('utf-8')

def handle_client_connection(client_socket):
    """
    Handles a single client connection
    """
    try:
        # Set a longer timeout for large files
        client_socket.settimeout(30)
        
        # Receive and process the request
        request_data = receive_http_request(client_socket)
        
        if request_data:
            # Clean the request data
            cleaned_request = parse_http_request(request_data)
            
            # Create and send response
            response = create_http_response(cleaned_request)
            client_socket.sendall(response)
    
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        client_socket.close()

def main():
    # Server configuration
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Define server address and port
    host = '127.0.0.1'  # localhost
    port = 8080
    
    try:
        # Bind socket to address and port
        server_socket.bind((host, port))
        # Start listening for connections
        server_socket.listen(5)
        print(f"Server listening on {host}:{port}")
        
        while True:
            try:
                # Accept client connections
                client_socket, client_address = server_socket.accept()
                print(f"Connection received from {client_address}")
                
                # Handle client in a separate function
                handle_client_connection(client_socket)
                    
            except Exception as e:
                print(f"Error accepting connection: {e}")
                
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main() 