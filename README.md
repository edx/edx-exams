# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/edx/edx-exams/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                  |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| edx\_exams/\_\_init\_\_.py                                                            |        1 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/\_\_init\_\_.py                                                       |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/\_\_init\_\_.py                                                   |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/constants.py                                                      |        1 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/models.py                                                         |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/permissions.py                                                    |       12 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/api/serializers.py                                                    |      129 |        0 |        8 |        0 |    100% |           |
| edx\_exams/apps/api/test\_utils/\_\_init\_\_.py                                       |       26 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/test\_utils/mixins.py                                             |       15 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/urls.py                                                           |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/v1/\_\_init\_\_.py                                                |       15 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/api/v1/tests/\_\_init\_\_.py                                          |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/v1/tests/test\_views.py                                           |      825 |        0 |      158 |       59 |     94% |261->266, 265->261, 266->265, 380->375, 406->405, 729->736, 735->729, 736->735, 778->783, 782->778, 783->782, 870->876, 875->870, 876->875, 883->896, 909->914, 913->909, 914->913, 923->936, 1004->1006, 1005->1004, 1006->1005, 1026->1030, 1027->1026, 1028->1027, 1029->1028, 1030->1029, 1050->1052, 1051->1050, 1052->1051, 1070->1069, 1080->1082, 1081->1080, 1082->1081, 1109->1112, 1110->1109, 1111->1110, 1112->1111, 1129->1132, 1130->1129, 1131->1130, 1132->1131, 1220->1229, 1227->1220, 1228->1227, 1229->1228, 1245->1251, 1249->1245, 1250->1249, 1251->1250, 1285->1284, 1318->1317, 1334->1340, 1338->1334, 1339->1338, 1340->1339, 1383->exit, 1397->exit, 1678->1677 |
| edx\_exams/apps/api/v1/urls.py                                                        |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/v1/views.py                                                       |      278 |        0 |       80 |        6 |     98% |103->102, 119->118, 133->132, 196->183, 337->336, 354->353 |
| edx\_exams/apps/core/\_\_init\_\_.py                                                  |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/api.py                                                           |      171 |        0 |       42 |        0 |    100% |           |
| edx\_exams/apps/core/apps.py                                                          |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/constants.py                                                     |        9 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/context\_processors.py                                           |        3 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/data.py                                                          |        7 |        0 |        2 |        0 |    100% |           |
| edx\_exams/apps/core/email.py                                                         |       36 |        0 |       10 |        0 |    100% |           |
| edx\_exams/apps/core/exam\_types.py                                                   |       35 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/core/exceptions.py                                                    |        7 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/\_\_init\_\_.py                                       |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/commands/\_\_init\_\_.py                              |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/commands/bulk\_add\_course\_staff.py                  |       27 |        0 |       10 |        2 |     95% |48->47, 56->59 |
| edx\_exams/apps/core/management/commands/test/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/commands/test/test\_bulk\_add\_course\_staff.py       |      112 |        0 |       34 |       16 |     89% |51->exit, 62->exit, 70->exit, 81->exit, 91->exit, 93->91, 100->exit, 102->100, 110->exit, 112->110, 120->exit, 135->exit, 137->135, 147->exit, 162->exit, 177->exit |
| edx\_exams/apps/core/migrations/0001\_initial.py                                      |        8 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0002\_create\_exam\_models.py                         |        8 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0003\_allow\_null\_provider.py                        |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0004\_alter\_exam\_unique\_together.py                |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0005\_user\_lms\_user\_id.py                          |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0006\_alter\_courseexamconfiguration\_course\_id.py   |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0007\_alter\_proctoringprovider\_name.py              |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0008\_allow\_null\_provider.py                        |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0009\_alter\_exam\_exam\_type.py                      |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0010\_remove\_user\_anonymous\_user\_id.py            |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0011\_user\_anonymous\_user\_id.py                    |       11 |        2 |        2 |        1 |     77% |     11-12 |
| edx\_exams/apps/core/migrations/0012\_alter\_exam\_unique\_together.py                |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0013\_alter\_choice\_fields.py                        |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0014\_historicalexam\_historicalexamattempt.py        |        9 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0015\_exam\_only one exam instance active.py          |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0016\_provider\_contact\_information.py               |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0017\_assessmentcontrolresult.py                      |        9 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0018\_staff\_roles.py                                 |        8 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0019\_alter\_user\_full\_name.py                      |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0020\_auto\_20231010\_1442.py                         |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0021\_alter\_exam\_exam\_types.py                     |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0022\_courseexamconfiguration\_escalation\_email.py   |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0023\_proctoringprovider\_tech\_support\_url.py       |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0024\_coursestaffrole\_role.py                        |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0025\_proctoringprovider\_org\_key.py                 |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0026\_studentallowance.py                             |        8 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0027\_coursestaffrole\_unique\_course\_staff\_role.py |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/\_\_init\_\_.py                                       |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/models.py                                                        |      204 |        0 |       48 |       17 |     93% |36->35, 170->169, 226->225, 237->236, 248->247, 269->268, 281->280, 348->347, 358->360, 359->358, 360->359, 395->394, 411->410, 458->457, 467->470, 478->477, 486->485 |
| edx\_exams/apps/core/rest\_utils.py                                                   |       11 |        0 |        2 |        0 |    100% |           |
| edx\_exams/apps/core/signals/\_\_init\_\_.py                                          |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/signals/signals.py                                               |       21 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/statuses.py                                                      |       29 |        0 |        8 |        3 |     92% |60->59, 68->67, 75->74 |
| edx\_exams/apps/core/test\_utils/factories.py                                         |       77 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/tests/\_\_init\_\_.py                                            |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_api.py                                               |      343 |        0 |       86 |       38 |     91% |176->181, 180->176, 181->180, 188->196, 195->188, 196->195, 246->239, 258->exit, 269->exit, 285->281, 291->exit, 322->exit, 328->335, 334->328, 335->334, 340->exit, 371->374, 376->380, 379->376, 380->379, 391->393, 406->408, 458->457, 485->481, 519->exit, 548->544, 565->568, 570->579, 578->570, 579->578, 608->611, 628->631, 671->670, 878->exit, 887->exit, 897->exit, 906->exit, 962->961 |
| edx\_exams/apps/core/tests/test\_context\_processors.py                               |        8 |        0 |        2 |        1 |     90% |    14->13 |
| edx\_exams/apps/core/tests/test\_email.py                                             |       57 |        0 |       26 |       10 |     88% |36->35, 42->48, 47->42, 48->47, 57->64, 63->57, 64->63, 88->87, 92->94, 105->97 |
| edx\_exams/apps/core/tests/test\_handlers.py                                          |       54 |        0 |       20 |        8 |     89% |51->50, 68->67, 79->89, 88->79, 89->88, 105->113, 112->105, 113->112 |
| edx\_exams/apps/core/tests/test\_models.py                                            |      100 |        0 |        6 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_views.py                                             |       37 |        0 |        6 |        3 |     93% |25->exit, 49->48, 55->54 |
| edx\_exams/apps/core/views.py                                                         |       42 |        0 |        8 |        1 |     98% |    48->39 |
| edx\_exams/apps/lti/\_\_init\_\_.py                                                   |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/apps.py                                                           |        6 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/migrations/\_\_init\_\_.py                                        |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/\_\_init\_\_.py                                           |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/handlers.py                                               |       23 |        0 |        6 |        1 |     97% |    17->16 |
| edx\_exams/apps/lti/signals/tests/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/tests/test\_handlers.py                                   |       54 |        0 |       14 |        6 |     91% |80->83, 81->80, 82->81, 83->82, 99->98, 115->114 |
| edx\_exams/apps/lti/tests/\_\_init\_\_.py                                             |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/tests/test\_views.py                                              |      272 |        0 |       84 |       36 |     90% |145->161, 157->145, 158->157, 159->158, 160->159, 161->160, 180->183, 181->180, 182->181, 183->182, 201->213, 209->201, 210->209, 211->210, 212->211, 213->212, 245->254, 250->245, 251->250, 252->251, 253->252, 254->253, 280->283, 281->280, 282->281, 283->282, 304->320, 316->304, 317->316, 318->317, 319->318, 320->319, 530->534, 554->558, 561->565, 716->719 |
| edx\_exams/apps/lti/urls.py                                                           |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/views.py                                                          |      166 |        0 |       78 |       24 |     90% |46->50, 47->46, 48->47, 49->48, 50->49, 190->194, 191->190, 192->191, 193->192, 194->193, 274->278, 275->274, 276->275, 277->276, 278->277, 344->348, 345->344, 346->345, 347->346, 348->347, 385->388, 386->385, 387->386, 388->387 |
| edx\_exams/apps/router/\_\_init\_\_.py                                                |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/router/interop.py                                                     |       58 |        0 |        8 |        0 |    100% |           |
| edx\_exams/apps/router/middleware.py                                                  |       18 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/router/tests/test\_interop.py                                         |       70 |        0 |       42 |       20 |     82% |37->36, 47->50, 48->47, 49->48, 50->49, 70->73, 71->70, 72->71, 73->72, 95->98, 96->95, 97->96, 98->97, 117->119, 118->117, 119->118, 136->139, 137->136, 138->137, 139->138 |
| edx\_exams/apps/router/tests/test\_views.py                                           |      124 |        0 |       22 |        9 |     94% |69->68, 121->120, 138->137, 170->169, 193->192, 237->236, 250->249, 307->306, 318->317 |
| edx\_exams/apps/router/views.py                                                       |       39 |        1 |        6 |        0 |     98% |        56 |
| edx\_exams/urls.py                                                                    |       14 |        0 |        0 |        0 |    100% |           |
|                                                                             **TOTAL** | **3697** |    **3** |  **834** |  **261** | **94%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/edx/edx-exams/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/edx/edx-exams/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/edx/edx-exams/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/edx/edx-exams/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fedx%2Fedx-exams%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/edx/edx-exams/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.