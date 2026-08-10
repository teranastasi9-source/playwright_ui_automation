# Self-hosted OrangeHRM for this test suite - wraps the official image with an
# entrypoint that runs OrangeHRM's own unattended CLI installer on first start,
# instead of depending on the shared opensource-demo.orangehrmlive.com instance.
# See README's "Self-hosted OrangeHRM" section for why.
FROM orangehrm/orangehrm

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
