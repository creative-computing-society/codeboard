from bs4 import BeautifulSoup

def parse_leetcode_data(username):
    with open(f'test_user_data/{username}_profile.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    user_data = {}

    user_data['username'] = username

    ranking_section = soup.find('span', class_ = 'ttext-label-1 dark:text-dark-label-1 font-medium')
    if ranking_section:
        user_data['ranking'] = ranking_section.text.strip()

    questions_solved_section = soup.find('div', class_ = 'text-[30px] font-semibold leading-[32px]')
    if questions_solved_section:
        user_data['numq'] = questions_solved_section.text.strip()


    return user_data

username = 'singlaishan69'
profile_data = parse_leetcode_data(username)
print(profile_data)