"""Use the pilot's real disclosure controls when a shared browser suite needs them."""
def control(page, selector):
    target=page.locator(selector)
    if target.count() and not target.first.is_visible():
        details=target.first.locator('xpath=ancestor::details[1]')
        if details.count() and details.is_visible() and details.get_attribute('open') is None:
            details.locator(':scope > summary').click()
    return target
