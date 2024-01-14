import webbrowser


def open_transaction_page(recipient_name, amount):
    address = "0x6a193214a872b219"
    base_url = "https://f7zl4z.csb.app/"
    url_with_params = f"{base_url}?recipient={address}&amount={amount}"
    webbrowser.open(url_with_params)

# open_transaction_page("Ian", 0.5)