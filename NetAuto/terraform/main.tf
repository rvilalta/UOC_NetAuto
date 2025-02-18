provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "csr_router" {
  ami           = "ami-0c55b159cbfafe1f0"  # Ex. Amazon Linux 2, substituir per la imatge CSR
  instance_type = "c5.large"

  tags = {
    Name = "MyCSRRouter"
  }
}
