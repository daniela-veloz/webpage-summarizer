import gradio as gr


class IPExtractor:
    @staticmethod
    def get_client_ip(request: gr.Request = None) -> str:
        """Extract client IP address from Gradio request object"""
        client_ip = "127.0.0.1"  # Default fallback
        
        if request and hasattr(request, 'client') and request.client:
            client_ip = request.client.host
        elif request and hasattr(request, 'headers'):
            # Try to get real IP from headers (for Hugging Face Spaces)
            client_ip = (
                request.headers.get('x-forwarded-for', '').split(',')[0].strip() or
                request.headers.get('x-real-ip', '').strip() or
                request.headers.get('cf-connecting-ip', '').strip() or
                "127.0.0.1"
            )
        
        return client_ip