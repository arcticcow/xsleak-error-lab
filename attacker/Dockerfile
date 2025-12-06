FROM nginx:1.25-alpine

# Remove default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy our static HTML into the Nginx web root.  The configuration
# installed in the base image already serves files from
# /usr/share/nginx/html.
COPY index.html /usr/share/nginx/html/index.html

# Expose port 80 (internal).  docker-compose will map this to a
# host port.
EXPOSE 80