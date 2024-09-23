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
| edx\_exams/apps/api/v1/tests/test\_views.py                                           |      825 |        0 |      158 |        0 |    100% |           |
| edx\_exams/apps/api/v1/urls.py                                                        |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/api/v1/views.py                                                       |      278 |        0 |       80 |        0 |    100% |           |
| edx\_exams/apps/core/\_\_init\_\_.py                                                  |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/api.py                                                           |      172 |        0 |       44 |        0 |    100% |           |
| edx\_exams/apps/core/apps.py                                                          |        5 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/constants.py                                                     |        9 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/context\_processors.py                                           |        3 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/data.py                                                          |        7 |        0 |        2 |        0 |    100% |           |
| edx\_exams/apps/core/email.py                                                         |       36 |        0 |       10 |        0 |    100% |           |
| edx\_exams/apps/core/exam\_types.py                                                   |       35 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/core/exceptions.py                                                    |        7 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/\_\_init\_\_.py                                       |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/commands/\_\_init\_\_.py                              |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/commands/bulk\_add\_course\_staff.py                  |       38 |        3 |       10 |        0 |     94% |     75-80 |
| edx\_exams/apps/core/management/commands/test/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/management/commands/test/test\_bulk\_add\_course\_staff.py       |      112 |        0 |       34 |        0 |    100% |           |
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
| edx\_exams/apps/core/migrations/0028\_admin\_optional\_fields.py                      |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/migrations/\_\_init\_\_.py                                       |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/models.py                                                        |      204 |        0 |       48 |        1 |     99% |  467->470 |
| edx\_exams/apps/core/rest\_utils.py                                                   |       11 |        0 |        2 |        0 |    100% |           |
| edx\_exams/apps/core/signals/\_\_init\_\_.py                                          |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/signals/signals.py                                               |       21 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/statuses.py                                                      |       29 |        0 |        8 |        0 |    100% |           |
| edx\_exams/apps/core/test\_utils/factories.py                                         |       77 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/tests/\_\_init\_\_.py                                            |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_api.py                                               |      352 |        0 |       88 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_context\_processors.py                               |        8 |        0 |        2 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_email.py                                             |       57 |        0 |       26 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_handlers.py                                          |       67 |        0 |       20 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_models.py                                            |      100 |        0 |        6 |        0 |    100% |           |
| edx\_exams/apps/core/tests/test\_views.py                                             |       37 |        0 |        6 |        0 |    100% |           |
| edx\_exams/apps/core/views.py                                                         |       42 |        0 |        8 |        0 |    100% |           |
| edx\_exams/apps/lti/\_\_init\_\_.py                                                   |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/apps.py                                                           |        6 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/migrations/\_\_init\_\_.py                                        |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/\_\_init\_\_.py                                           |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/handlers.py                                               |       23 |        0 |        6 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/tests/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/signals/tests/test\_handlers.py                                   |       54 |        0 |       14 |        0 |    100% |           |
| edx\_exams/apps/lti/tests/\_\_init\_\_.py                                             |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/tests/test\_views.py                                              |      272 |        0 |       84 |        0 |    100% |           |
| edx\_exams/apps/lti/urls.py                                                           |        4 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/lti/views.py                                                          |      166 |        0 |       78 |        0 |    100% |           |
| edx\_exams/apps/router/\_\_init\_\_.py                                                |        0 |        0 |        0 |        0 |    100% |           |
| edx\_exams/apps/router/interop.py                                                     |       58 |        0 |        8 |        0 |    100% |           |
| edx\_exams/apps/router/middleware.py                                                  |       18 |        0 |        4 |        0 |    100% |           |
| edx\_exams/apps/router/tests/test\_interop.py                                         |       70 |        0 |       42 |        0 |    100% |           |
| edx\_exams/apps/router/tests/test\_views.py                                           |      124 |        0 |       22 |        0 |    100% |           |
| edx\_exams/apps/router/views.py                                                       |       39 |        1 |        6 |        0 |     98% |        56 |
| edx\_exams/urls.py                                                                    |       14 |        0 |        0 |        0 |    100% |           |
|                                                                             **TOTAL** | **3735** |    **6** |  **838** |    **2** | **99%** |           |


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