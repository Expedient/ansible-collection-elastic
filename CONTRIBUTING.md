# Quick-start development guide
<!-- This content is being put together from several different sources included below

https://github.com/ansible/community-docs/blob/main/create_pr_quick_start_guide.rst

-->

This guide describes all steps needed to create your first patch and submit a pull request.

## Prepare your environment

We assume that you use Linux as a work environment (you can use a virtual machine as well) and have `git` installed.

1. If possible, make sure that you have installed and started `docker`. While you can also run tests without docker, this makes it a lot easier since you do not have to install the precise requirements, and tests are running properly isolated and in the exact same environments as in CI.

2. [Install](https://docs.ansible.com/ansible/devel/installation_guide/intro_installation.html) Ansible or ansible-core. You will need the  `ansible-test` utility which is provided by either of the packages.

3. Create the following directories in your home directory:
    ```
    mkdir -p ~/ansible_collections/NAMESPACE/COLLECTION_NAME
    ```
    For example, if the collection is `expedient.elastic`, it will be:
    ```
    mkdir -p ~/ansible_collections/expedient/elastic
    ```
4. Fork the collection repository through the GitHub web interface.

5. Clone the forked repository from your profile to the created path:
    ```
    git clone https://github.com/YOURACC/COLLECTION_REPO.git ~/ansible_collections/NAMESPACE/COLLECTION_NAME
    ```
    If you prefer to use the SSH protocol:
    ```
    git clone git@github.com:YOURACC/COLLECTION_REPO.git ~/ansible_collections/NAMESPACE/COLLECTION_NAME
    ```
6. Go to your new cloned repository.
    ```
    cd ~/ansible_collections/NAMESPACE/COLLECTION_NAME
    ```
7. Be sure you are in the default branch (it is usually `main`):
    ```
    git status
    ```
8. Show remotes. There should be the `origin` repository only:
    ```
    git remote -v
    ```
9. Add the `upstream` repository:
    ```
    git remote add upstream https://github.com/Expedient/COLLECTION_REPO.git
    ```
    This is the repository where you forked from.

10. Update your local default branch. Assuming that it is `main`:
    ```
    git fetch upstream
    git rebase upstream/main
    ```
11. Create a branch for your changes:
    ```
    git checkout -b name_of_my_branch
    ```
## Change the code

### note
Do NOT mix several bugfixes or features that are not tightly-related in one pull request. Use separate pull requests for different changes.

12. Fix the bug or add the feature.

## Test your changes

13. Run `flake8` against a changed file:
    ```
    flake8 path/to/changed_file.py
    ```
    It is worth installing (`pip install flake8`, or install the corresponding package on your operating system) and running `flake8` against the changed file(s) first.
    It shows unused imports, which is not shown by sanity tests (see the next step), as well as other common issues.
    Optionally, you can use the `--max-line-length=160` command-line argument.

14. Run sanity tests:
    ```
    ansible-test sanity path/to/changed_file.py --docker -v
    ```
    If they failed, look at the output carefully - it is usually very informative and helps to identify a problem line quickly.
    Sanity failings usually relate to wrong code and documentation formatting.

## Submit a pull request

15. Commit your changes with an informative but short commit message:
    ```
    git add /path/to/changed/file
    git commit -m "module_name_you_fixed: fix crash when ..."
    ```
16. Push the branch to the `origin` (your fork):
    ```
    git push origin name_of_my_branch
    ```
17. In a browser, navigate to the `upstream` repository (http://github.com/Expedient/COLLECTION_REPO).

18. Click the `Pull requests` tab.

    GitHub is tracking your fork, so it should see the new branch in it and automatically offer
    to create a pull request. Sometimes GitHub does not do it, and you should click the `New pull request` button yourself.
    Then choose `compare across forks` under the `Compare changes` title.
    Choose your repository and the new branch you pushed in the right drop-down list. Confirm.

    Fill out the pull request template with all information you want to mention.

    Put `Fixes + link to the issue` in the pull request's description.

    Put `[WIP] + short description` in the pull request's title. It's often a good idea to mention the name of the module/plugin you are modifying at the beginning of the description.

    Click `Create pull request`.

19. The CI tests will run automatically after every commit.
    You will see the CI status in the bottom of your pull request.
    If they are green and you think that you do not want to add more commits before someone should take a closer look at it, remove `[WIP]` from the title. Mention the issue reporter in a comment and let contributors know that the pull request is "Ready for review".

20. Wait for reviews.

21. If the pull request looks good to the community, committers will merge it.

For details, refer to the [Ansible developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html).


# Additional Tools
* For generating the documentation RST files, use [`collection_prep_add_docs -p .`](https://github.com/ansible-network/collection_prep) inside the collection directory. This step should be performed after running `ansible-test` to ensure documentation is up-to-date.
  * When updating `doc_fragments` for `module_utils`, you may need to run the above command twice or install the collection if you are not developing in your `COLLECTIONS_PATH`. 