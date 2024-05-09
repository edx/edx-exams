from lti_consumer.models import LtiConfiguration
	
consumer = LtiConfiguration.objects.get(id=1).get_lti_consumer()
print(consumer.client_id)
