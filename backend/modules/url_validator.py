from urllib.parse import urlparse


class URLValidator:
    def validate(self, url: str) -> str:
        """
        Validates that the URL is a valid GitHub HTTPS URL.
        Returns the cleaned URL if valid, otherwise raises ValueError.
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        parsed = urlparse(url)

        if parsed.scheme not in ["http", "https"]:
            raise ValueError("Only HTTP/HTTPS GitHub URLs are supported")

        if "github.com" not in parsed.netloc:
            raise ValueError("URL must point to github.com")

        # Remove trailing slashes
        return url.rstrip("/")
