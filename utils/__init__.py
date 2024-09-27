

def remove_scheme(url):
    if url.startswith('http://'):
        return url[len('http://'):]
    elif url.startswith('https://'):
        return url[len('https://'):]
    return url


def is_internal_link(url, current_domain, base_path):
    parsed_url = urlparse(url)
    if parsed_url.netloc == '':
        return True  # Relative path
    if current_domain in parsed_url.netloc and parsed_url.path.startswith(base_path):
        return True  # Same domain or subdomain and within the base path
    return False
