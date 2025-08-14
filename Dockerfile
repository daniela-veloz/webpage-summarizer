FROM python:3.9

RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    ffmpeg \
    libsm6 \
    libxext6 \
    cmake \
    rsync \
    libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# Create a user with proper permissions
RUN useradd -m -u 1000 user

# Set up directories with proper permissions
WORKDIR /app
RUN chown -R user:user /app

# Create Streamlit config directory in user home
RUN mkdir -p /home/user/.streamlit && chown -R user:user /home/user/.streamlit

# Switch to user before installing dependencies
USER user
ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH

# Copy and install requirements
COPY --chown=user:user requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=user:user . .

# Create rate limits directory with proper permissions
RUN mkdir -p /app/.rate_limits
RUN mkdir -p /app/.cache

# Disable Streamlit usage stats collection
ENV STREAMLIT_SERVER_GATHER_USAGE_STATS=false

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]