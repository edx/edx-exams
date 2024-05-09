from openedx_filters import PipelineStep

class GetLtiConfigurations(PipelineStep):
    def run_filter(
        self, context, config_id, configurations, *args, **kwargs
    ):
        return {
            'configurations': {
                config_id: {
                    'lti_1p3_client_id': '1234'
                }
            }
        }