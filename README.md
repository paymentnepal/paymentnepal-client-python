API client for Alba
=============

API client implements two basic classes AlbaService and AlbaCallback to inherit.

AlbaService is a service in Alba. It allows getting list of available payment methods, init transactions, get transaction info. For that purpose a single instance for each service needs to be created.

AlbaCallback - callback handler for Alba. Checks electronic sign and calls method relevant to "command" value.

During work an AlbaException can be raised.

Example of using API client to init transaction:

       from alba_client import AlbaService, AlbaException

       service = AlbaService(<service-id>, '<service-secret>')
       try:
           response = service.init_payment('mc', 10, 'Test', 'test@example.com', '71111111111')
       except AlbaException, e:
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

       from alba_client import AlbaCallback

       class MyAlbaCallback(AlbaCallback):
           def callback_success(self, data):
               # settle a successful transaction

       service1 = AlbaService(<service1-id>, '<service1-secret>')
       service2 = AlbaService(<service2-id>, '<service2-secret>')
       callback = MyAlbaCallback([service1, service2])
       callback.handle(<POST-data-dict>)
       



