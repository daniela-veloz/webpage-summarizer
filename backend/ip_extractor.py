import logging
import streamlit as st

class IPExtractor:
    """
    Utility class for extracting client IP addresses from Streamlit context.
    
    This class provides methods to extract the real client IP address from
    various HTTP headers, with fallback mechanisms for different deployment
    scenarios including local development and cloud hosting.
    
    Attributes:
        logger (logging.Logger): Logger instance for debugging
        DEFAULT_IP_ADDRESS (str): Fallback IP address for local development
    """
    logger = logging.getLogger(__name__)
    DEFAULT_IP_ADDRESS = "127.0.0.1"

    @staticmethod
    def get_client_ip() -> str:
        """
        Extract client IP address from Streamlit context.
        
        Attempts to extract the real client IP address from various HTTP headers
        including x-forwarded-for, x-real-ip, and cf-connecting-ip. Falls back
        to a default IP address if extraction fails or in local development.
        
        Returns:
            str: The client IP address, or default IP if extraction fails
        """
        client_ip = IPExtractor.DEFAULT_IP_ADDRESS  # Default fallback
        IPExtractor.logger.debug("Extracting IP from Streamlit context")

        try:
            # Try to get IP from Streamlit context
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                headers = st.context.headers
                client_ip = (
                    headers.get('x-forwarded-for', '').split(',')[0].strip() or
                    headers.get('x-real-ip', '').strip() or
                    headers.get('cf-connecting-ip', '').strip() or
                    IPExtractor.DEFAULT_IP_ADDRESS
                )
                IPExtractor.logger.info(f"Extracted IP from headers: {client_ip}")
            else:
                # Fallback: try to get from session state or other Streamlit mechanisms
                if 'client_ip' in st.session_state:
                    client_ip = st.session_state.client_ip
                else:
                    # Use default IP for local development
                    client_ip = IPExtractor.DEFAULT_IP_ADDRESS
                    IPExtractor.logger.info(f"Using default IP: {client_ip}")
        except Exception as e:
            IPExtractor.logger.warning(f"Failed to extract IP: {e}, using default")
            client_ip = IPExtractor.DEFAULT_IP_ADDRESS
        
        IPExtractor.logger.debug(f"Final extracted IP: {client_ip}")
        return client_ip