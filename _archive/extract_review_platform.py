from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.browser import create_browser
from core.filesystem import save_html
from core.logger import Logger
from _archive.scrolling import scroll_until_complete


logger = Logger(__name__)



def build_review_url(
    game: str,
    review_type: str,
    platform: str
):

    return (
        f"https://www.metacritic.com/game/{game}/"
        f"{review_type}-reviews/"
        f"?platform={platform}"
    )



def extract_review_page(
    game: str,
    review_type: str,
    platform: str
):


    logger.info(
        f"Extraction : {game} - {review_type} - {platform}"
    )


    url = build_review_url(
        game,
        review_type,
        platform
    )


    logger.info(
        url
    )


    session = None


    try:


        session = create_browser(
            headless=True
        )


        page = session.page


        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )


        logger.info(
            "Page chargée"
        )



        try:


            page.wait_for_selector(
                '[data-testid="review-card"]',
                timeout=5000
            )


            logger.info(
                "Premières reviews détectées"
            )


        except PlaywrightTimeoutError:


            logger.warning(
                "Aucune review trouvée"
            )


            return None



        logger.info(
            "Chargement des reviews..."
        )


        scroll_until_complete(
            page,
            '[data-testid="review-card"]'
        )



        count = page.locator(
            '[data-testid="review-card"]'
        ).count()


        logger.info(
            f"Reviews finales : {count}"
        )



        html = page.content()


        output = save_html(
            game,
            review_type,
            platform,
            html
        )


        logger.info(
            f"HTML sauvegardé : {output}"
        )


        return output



    except Exception as error:


        logger.error(
            f"Erreur extraction : {error}"
        )


        return None



    finally:


        if session:

            session.close()