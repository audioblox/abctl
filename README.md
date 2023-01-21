# ADMIN ONLY

## DEPLOY

1. Merge `main` as normal
2. `git tag v1.0.0 && git push v1.0.0`
3. Wait for github actions to package the release
4. Go to the release, right click on `abctl.tar.gz` and copy link
5. `brew create [link to abctl.tar.gz copied from step 4]`