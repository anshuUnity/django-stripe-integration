from django.http.response import HttpResponse
from django.shortcuts import render
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1J2CsqC3Qbp2OE6oBbnQZyGo',
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://127.0.0.1:8000/'

    )

    context = {
        'session_id': session.id,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, 'index.html', context=context)


def thanks(request):
    return HttpResponse('YOUR PAYMENT IS SUCCESSFULL')


@csrf_exempt
def stripe_webhook(request):

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    print('WEBHOOK!')
    # You can find your endpoint's secret in your webhook settings whsec_fGbxm8HpKgqntQG3SAuKxFLPm80d1dNa
    endpoint_secret = 'whsec_fGbxm8HpKgqntQG3SAuKxFLPm80d1dNa'

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(
            session['id'], limit=1)
        print(line_items)

    return HttpResponse(status=200)
