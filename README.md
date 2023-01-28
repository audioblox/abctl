# ADMIN ONLY

## DEPLOY [WIP]

1. Merge `main` as normal
2. `git tag v1.0.0 && git push v1.0.0`
3. Wait for github actions to package the release
4. Go to the release, right click on `abctl.tar.gz` and copy link
5. `brew create [link to abctl.tar.gz copied from step 4]`
6. If it errors on an existing file, remove the original file and run the command again
7. Open the created file (if not opened automatically)
8. Copy the url, and sha
9. Go to `audioblox/homebrew-audioblox/abctl.rb`, and past the url and sha
10. Copy the entire `audioblox/homebrew-audioblox/abctl.rb` file and paste it in the file brew created, removing all original content
11. Push the changes to main:
12. `cd ../homebrew-audioblox && git commit -am "Update" && git push && cd ../abctl`
13. [OPTIONAL] Ensure you have an env set to the userfile location. `export ABCTL_ROOT_DIR=~/.abctluser`
14. `brew uninstall --force abctl`
15. `rm -rf /usr/local/Homebrew/Library/Taps/audioblox`
16. `brew tap audioblox/audioblox`
17. `brew install --build-from-source abctl`
