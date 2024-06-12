# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/edx/edx-exams/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------------------------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| edx\_exams/\_\_init\_\_.py                                                          |        1 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/\_\_init\_\_.py                                                     |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/constants.py                                                    |        1 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/models.py                                                       |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/permissions.py                                                  |       12 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/api/serializers.py                                                  |      114 |        0 |        6 |        0 |    100% |           |
| edx\_exams/apps/api/test\_utils/\_\_init\_\_.py                                     |       26 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/test\_utils/mixins.py                                           |       15 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/urls.py                                                         |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/v1/\_\_init\_\_.py                                              |       15 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/api/v1/tests/\_\_init\_\_.py                                        |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/v1/tests/test\_views.py                                         |      735 |        0 |      152 |       59 |     93% |253->258, 257->253, 258->257, 372->367, 398->397, 721->728, 727->721, 728->727, 770->775, 774->770, 775->774, 862->868, 867->862, 868->867, 875->888, 901->906, 905->901, 906->905, 915->928, 996->998, 997->996, 998->997, 1018->1022, 1019->1018, 1020->1019, 1021->1020, 1022->1021, 1042->1044, 1043->1042, 1044->1043, 1062->1061, 1072->1074, 1073->1072, 1074->1073, 1101->1104, 1102->1101, 1103->1102, 1104->1103, 1121->1124, 1122->1121, 1123->1122, 1124->1123, 1212->1221, 1219->1212, 1220->1219, 1221->1220, 1237->1243, 1241->1237, 1242->1241, 1243->1242, 1277->1276, 1310->1309, 1326->1332, 1330->1326, 1331->1330, 1332->1331, 1375->exit, 1389->exit, 1656->1655 |
| edx\_exams/apps/api/v1/urls.py                                                      |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/v1/views.py                                                     |      248 |        0 |       74 |        6 |     98% |95->94, 111->110, 125->124, 188->175, 329->328, 346->345 |
| edx\_exams/apps/core/\_\_init\_\_.py                                                |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/api.py                                                         |      168 |        0 |       40 |        0 |    100% |           |
| edx\_exams/apps/core/apps.py                                                        |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/constants.py                                                   |        8 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/context\_processors.py                                         |        3 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/data.py                                                        |        7 |        0 |        2 |        0 |    100% |           |
| edx\_exams/apps/core/email.py                                                       |       36 |        0 |       10 |        0 |    100% |           |
| edx\_exams/apps/core/exam\_types.py                                                 |       35 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/core/exceptions.py                                                  |        7 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/commands/\_\_init\_\_.py                            |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/commands/bulk\_add\_course\_staff.py                |       35 |        0 |       16 |        2 |     96% |48->47, 56->59 |
| edx\_exams/apps/core/management/commands/test/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/commands/test/test\_bulk\_add\_course\_staff.py     |       84 |        0 |       22 |       10 |     91% |51->exit, 62->exit, 70->exit, 81->exit, 91->exit, 93->91, 101->exit, 116->exit, 118->116, 128->exit |
| edx\_exams/apps/core/migrations/0001\_initial.py                                    |        8 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0002\_create\_exam\_models.py                       |        8 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0003\_allow\_null\_provider.py                      |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0004\_alter\_exam\_unique\_together.py              |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0005\_user\_lms\_user\_id.py                        |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0006\_alter\_courseexamconfiguration\_course\_id.py |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0007\_alter\_proctoringprovider\_name.py            |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0008\_allow\_null\_provider.py                      |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0009\_alter\_exam\_exam\_type.py                    |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0010\_remove\_user\_anonymous\_user\_id.py          |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0011\_user\_anonymous\_user\_id.py                  |       11 |        2 |        2 |        1 |     77% |     11-12 |
| edx\_exams/apps/core/migrations/0012\_alter\_exam\_unique\_together.py              |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0013\_alter\_choice\_fields.py                      |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0014\_historicalexam\_historicalexamattempt.py      |        9 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0015\_exam\_only one exam instance active.py        |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0016\_provider\_contact\_information.py             |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0017\_assessmentcontrolresult.py                    |        9 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0018\_staff\_roles.py                               |        8 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0019\_alter\_user\_full\_name.py                    |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0020\_auto\_20231010\_1442.py                       |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0021\_alter\_exam\_exam\_types.py                   |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0022\_courseexamconfiguration\_escalation\_email.py |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0023\_proctoringprovider\_tech\_support\_url.py     |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0024\_coursestaffrole\_role.py                      |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/0025\_proctoringprovider\_org\_key.py               |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/models.py                                                      |      177 |        0 |       40 |       13 |     94% |35->34, 164->163, 220->219, 231->230, 242->241, 263->262, 275->274, 342->341, 352->354, 353->352, 354->353, 389->388, 405->404 |
| edx\_exams/apps/core/rest\_utils.py                                                 |       11 |        0 |        2 |        0 |    100% |           |
| edx\_exams/apps/core/signals/\_\_init\_\_.py                                        |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/signals/signals.py                                             |       21 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/statuses.py                                                    |       29 |        0 |        8 |        3 |     92% |60->59, 68->67, 75->74 |
| edx\_exams/apps/core/test\_utils/factories.py                                       |       71 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/tests/\_\_init\_\_.py                                          |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_api.py                                             |      335 |        0 |       84 |       37 |     91% |175->180, 179->175, 180->179, 187->195, 194->187, 195->194, 245->238, 257->exit, 268->264, 274->exit, 305->exit, 311->318, 317->311, 318->317, 323->exit, 354->357, 359->363, 362->359, 363->362, 374->376, 389->391, 441->440, 468->464, 502->exit, 531->527, 548->551, 553->562, 561->553, 562->561, 591->594, 611->614, 654->653, 861->exit, 870->exit, 880->exit, 889->exit, 945->944 |
| edx\_exams/apps/core/tests/test\_context\_processors.py                             |        8 |        0 |        2 |        1 |     90% |    14->13 |
| edx\_exams/apps/core/tests/test\_email.py                                           |       57 |        0 |       26 |       10 |     88% |36->35, 42->48, 47->42, 48->47, 57->64, 63->57, 64->63, 88->87, 92->94, 105->97 |
| edx\_exams/apps/core/tests/test\_handlers.py                                        |       54 |        0 |       20 |        8 |     89% |51->50, 68->67, 79->89, 88->79, 89->88, 105->113, 112->105, 113->112 |
| edx\_exams/apps/core/tests/test\_models.py                                          |       72 |        0 |        6 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_views.py                                           |       37 |        0 |        6 |        3 |     93% |25->exit, 49->48, 55->54 |
| edx\_exams/apps/core/views.py                                                       |       42 |        0 |        8 |        1 |     98% |    48->39 |
| edx\_exams/apps/lti/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/apps.py                                                         |        6 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/migrations/\_\_init\_\_.py                                      |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/\_\_init\_\_.py                                         |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/handlers.py                                             |       23 |        0 |        6 |        1 |     97% |    17->16 |
| edx\_exams/apps/lti/signals/tests/\_\_init\_\_.py                                   |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/tests/test\_handlers.py                                 |       54 |        0 |       14 |        6 |     91% |80->83, 81->80, 82->81, 83->82, 99->98, 115->114 |
| edx\_exams/apps/lti/tests/\_\_init\_\_.py                                           |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/tests/test\_views.py                                            |      272 |        0 |       84 |       36 |     90% |145->161, 157->145, 158->157, 159->158, 160->159, 161->160, 180->183, 181->180, 182->181, 183->182, 201->213, 209->201, 210->209, 211->210, 212->211, 213->212, 245->254, 250->245, 251->250, 252->251, 253->252, 254->253, 280->283, 281->280, 282->281, 283->282, 304->320, 316->304, 317->316, 318->317, 319->318, 320->319, 530->534, 554->558, 561->565, 716->719 |
| edx\_exams/apps/lti/urls.py                                                         |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/views.py                                                        |      166 |        0 |       78 |       24 |     90% |46->50, 47->46, 48->47, 49->48, 50->49, 190->194, 191->190, 192->191, 193->192, 194->193, 274->278, 275->274, 276->275, 277->276, 278->277, 344->348, 345->344, 346->345, 347->346, 348->347, 385->388, 386->385, 387->386, 388->387 |
| edx\_exams/apps/router/\_\_init\_\_.py                                              |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/router/interop.py                                                   |       58 |        0 |        8 |        0 |    100% |           |
| edx\_exams/apps/router/middleware.py                                                |       18 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/router/tests/test\_interop.py                                       |       70 |        0 |       42 |       20 |     82% |37->36, 47->50, 48->47, 49->48, 50->49, 70->73, 71->70, 72->71, 73->72, 95->98, 96->95, 97->96, 98->97, 117->119, 118->117, 119->118, 136->139, 137->136, 138->137, 139->138 |
| edx\_exams/apps/router/tests/test\_views.py                                         |      124 |        0 |       22 |        9 |     94% |69->68, 121->120, 138->137, 170->169, 193->192, 237->236, 250->249, 307->306, 318->317 |
| edx\_exams/apps/router/views.py                                                     |       39 |        1 |        6 |        0 |     98% |        56 |
| edx\_exams/urls.py                                                                  |       14 |        0 |        0 |        0 |    100% |           |
|                                                                           **TOTAL** | **3457** |    **3** |  **802** |  **250** | **94%** |           |


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