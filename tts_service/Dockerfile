# Phase 1: Base Image
# Use official AMD ROCm image that includes Python 3.11 and a compatible PyTorch.
FROM rocm/pytorch:rocm6.1.1-runtime-pytorch2.2.1-py3.11

# Phase 2: System Setup
# Set a working directory inside the container.
WORKDIR /app

# Install system-level dependencies required by our Python packages.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    espeak-ng \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

# Phase 3: Install Python Dependencies
# Copy only the requirements file first to leverage Docker's build cache.
COPY requirements.txt .

# Install the packages listed in requirements.txt.
# Note: torch and torchaudio are already in the base image.
RUN pip install --no-cache-dir -r requirements.txt

# Phase 4: Copy Application Code
# Copy the rest of our application's source code into the container.
COPY . .

# Phase 5: Set Default Command
# This is the command that will run when the container starts.
CMD ["python", "main.py"]