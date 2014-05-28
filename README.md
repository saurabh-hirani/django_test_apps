django_test_apps
================

Rationale:

I learnt django through the basic polling app as mentioned in the [django-docs](https://docs.djangoproject.com/en/1.6/intro/tutorial01/) and through Mike Hibbert's [[youtube videos](https://www.youtube.com/watch?v=oT1A1KKf0SI). This repository builds upon their ideas with the following additions:

- Generic features:

  - Login / logout functionality - no operation can be performed without logging in (e.g. voting for a poll)
  - Privileged user operations - only admin user will be shown link to create poll, only admin user can reopen a closed poll, etc.
  - Login home page with the facility to navigate to multiple apps. (as of writing this - Poll app is implemented, blogging app is a stub)
  - Using the very slick - session_security django module for session timeout.
  - Adding the awesomeness of jquery and bootstrap to the application.
  
- Polling app specific features:

  - All users are associated with a poll upon the poll's creation (auto registration of voters.)
  - A poll stays in open state till all users vote for its choices, after which poll is closed and results are displayed.
  - A dashboard for showing - open polls, closed polls and polls pending current user's votes with an interesting ability to:
    - Reopen a closed poll so as to restart voting afresh.
    - Vote randomly in a poll so as to close an open poll.
  - Using decorators to ensure authorization e.g.
    - A user can vote in a poll only if the poll is open and the user has not voted for it earlier.
    - A user can view results of a poll only if all the users have voted in the poll.
    - and so on...
  - Using TestCase to perform testing and the very useful coverage module to ensure code coverage.

The code in this repository is work in progress.
