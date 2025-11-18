from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_dynamic_email(request, email, fullname, task):
    context = {
        'user_name': fullname,
        'user_email': email,
        'site_name': 'MyAwesomeSite'
    }

    if task == 'welcome_email':
        html_content = render_to_string('emails/welcome_email.html', context)
    elif task == 'comment_added':
        html_content = render_to_string('emails/comment_added.html', context)

    text_content = strip_tags(html_content)  # Fallback text for plain email clients

    email = EmailMultiAlternatives(
        subject='Welcome to MyAwesomeSite!',
        body=text_content,
        from_email='ajaysappa10kcoders@gmail.com',
        to=[email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
