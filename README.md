API client for Paymentnepal
=============

API client implements two basic classes PaymentnepalService and PaymentnepalCallback to inherit.

PaymentnepalService is a service in Paymentnepal. It allows getting list of available payment methods, init transactions, get transaction info. For that purpose a single instance for each service needs to be created.

PaymentnepalCallback - callback handler for Paymentnepal. Checks electronic sign and calls method relevant to "command" value.

During work an PaymentnepalException can be raised.

Example of using API client to init transaction:

       from paymentnepal_client import PaymentnepalService, PaymentnepalException

       service = PaymentnepalService(<service-id>, '<service-secret>')
       try:
           response = service.init_payment('mc', 10, 'Test', 'test@example.com', '71111111111')
       except PaymentnepalException, e:
           print e
           
Checking if 3-D secure is needed:

       card3ds = response.get('3ds')
       if card3ds:
           # Требуется 3-D secure
           
If 3-D secure is needed a POST request to card3ds['ACSUrl'] is sent with next params:
       
       PaReq - with card3ds['PaReq'] value
       MD - with card3ds['MD'] value
       TermUrl - your site handler URL. Customer is redirected onto it after 3DS authorization at card issuer page. This URL needs to be formed to provide transaction info. Recommended are: service_id, tid and order_id (in case the transaction was created with it)
       

Example of using API client to use with callback:

       from alba_client import PaymentnepalCallback

       class MyPaymentnepalCallback(PaymentnepalCallback):
           def callback_success(self, data):
               # settle a successful transaction

       service1 = PaymentnepalService(<service1-id>, '<service1-secret>')
       service2 = PaymentnepalService(<service2-id>, '<service2-secret>')
       callback = MyPaymentnepalCallback([service1, service2])
       callback.handle(<POST-data-dict>)
       



