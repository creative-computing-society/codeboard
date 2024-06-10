from playwright.sync_api import sync_playwright

def save_leetcode_profile_html(username):
    url = f"https://leetcode.com/u/{username}/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set headless to False for debugging
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            bypass_csp=True
        )
        page = context.new_page()
        page.goto(url)

        # Wait for the page to fully load and pass Cloudflare verification
        page.wait_for_timeout(5000)

        html_content = page.content()
        with open(f'test_user_data/{username}_profile.html', 'w', encoding='utf-8') as file:
            file.write(html_content)

        print(f"Saved HTML content for {username} to {username}_profile.html")
        browser.close()

# Example usage
username = 'singlaishan69'
save_leetcode_profile_html(username)
