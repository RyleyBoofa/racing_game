import pygame


def scale_image(img, factor):
    """
    Scale an image scaled by 'factor' amount.
    :param img: pygame.image
    :param factor: Float scale factor.
    :return: Scaled image.
    """
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(window, image, top_left, angle):
    """
    Rotate an image around it's center point.
    :param window: Surface to draw rotated image.
    :param image: Image to be rotated.
    :param top_left: Original image's top-left position.
    :param angle: Target angle to rotate image to.
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    window.blit(rotated_image, new_rect.topleft)


def blit_text_center(window, font, text):
    """
    Print a message to the center of the screen.
    :param window: Surface to draw text to.
    :param font: Font with which the text is displayed.
    :param text: Text to be displayed.
    """
    render = font.render(text, 1, "grey")
    window.blit(
        render,
        (
            window.get_width() / 2 - render.get_width() / 2,
            window.get_height() / 2 - render.get_height() / 2,
        ),
    )
