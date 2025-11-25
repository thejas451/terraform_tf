# Use the official Terraform image as the "Application" base
FROM hashicorp/terraform:light
 
# Set the working directory inside the container
WORKDIR /app
 
# Copy your Terraform code into the container
COPY test.tf .
 
# When this container runs, it will default to showing help or running terraform
# (To actually run 'apply' later, you would provide credentials to this container)
ENTRYPOINT ["terraform"]
 
 