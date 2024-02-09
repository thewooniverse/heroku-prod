

## CI/CD - ELI5
Imagine you're building a really cool LEGO castle. CI/CD is like having an awesome set of tools and helpers to make building and showing off your castle easier and faster.

### CI: Continuous Integration

**CI is like cleaning up your LEGO pieces and checking they fit right after you play each time.**

- **Automated Checks**: Every time you add new LEGO pieces to your castle (like when you write new code), there's a system that automatically checks to make sure everything still fits together nicely. If a new piece doesn't fit, it tells you right away, so you can fix it before it becomes a big problem.
- **Sharing Pieces**: You and your friends are all adding pieces to the castle. CI helps by making sure that everyone's pieces are put together often, so your castle always looks cool and there are no surprises.

### CD: Continuous Deployment/Delivery

**CD is like showing your LEGO castle to your friends and family automatically every time it gets better.**

- **Automatic Updates**: Once all the new LEGO pieces fit perfectly (your code passes all checks), your castle gets updated in its display spot for everyone to see (your app gets updated for users). This can happen very often, even several times a day!
- **Safe and Sound**: Before your updated castle goes on display, it’s checked in a special room to make sure nothing falls apart when people look at it (like a staging environment). If something isn't right, it doesn't go on display until it's fixed.

### Putting It All Together

So, CI/CD is like having an automated system that helps you check your LEGO castle pieces as you build, making sure they fit, and then automatically putting your castle on display when it's ready. It makes building and sharing your castle faster, safer, and more fun, without waiting for a big reveal at the end.



### CI/CD Workflow:

1. **Branch Out**: You create a new feature branch from the main (or development) branch in your version control system. This is where you'll build your new feature or fix.

2. **Build and Test Locally**: Develop your code and perform local testing. This step might include unit tests, integration tests, and any other relevant checks to ensure your code works as expected.

3. **Push to Feature Branch**: Once you're satisfied with your local development and testing, you push your changes to the remote feature branch in your version control repository.

4. **Automated CI Checks**: Pushing your changes triggers the Continuous Integration (CI) pipeline. This usually involves automated tests running in a CI environment (which could be a service like GitHub Actions, GitLab CI/CD, Jenkins, etc.). These checks ensure that your new code integrates well with the existing codebase and that it doesn't introduce any regressions or failures.

5. **Pull Request (PR) / Merge Request (MR)**: After your feature branch passes all CI checks, you create a Pull Request (PR) or Merge Request (MR) to merge your feature branch into the main (or development) branch. This is a request for your team to review your changes.

6. **Code Review and Approval**: Your team reviews the changes in the PR/MR. They might suggest improvements or request changes. Once the PR/MR is approved by the required number of reviewers, it's ready to be merged.

7. **Merge to Main/Staging Branch**: After approval, you merge your feature branch into the main branch. This merge might trigger another round of CI checks to ensure that the merge doesn't introduce any issues.

8. **Staging Deployment**: The updated main branch is then deployed to a Staging environment. This environment is a close replica of the Production environment and is used for final testing and validation. This step might involve manual testing, user acceptance testing (UAT), or additional automated tests.

9. **Production Deployment**: Once the code in the Staging environment is verified and confirmed to be stable and functioning as expected, it's then deployed to the Production environment. This step makes the new features or fixes available to end-users.

10. **Monitoring and Feedback**: After deployment, continuous monitoring of the application in production is essential to quickly identify and address any issues that might arise. Feedback from this stage can lead to new improvements or features, restarting the cycle.

### Clarifications:

- The "staging" and "main" branches can be different based on your workflow. In some workflows, the main branch is directly used for production deployments, while in others, a separate branch (like "production") might be used for production deployments.
- The staging environment is typically used for final testing before production. It's not a separate branch but a deployment environment that mirrors production as closely as possible.
- The deployment to production can be automatic (Continuous Deployment) or require manual approval (Continuous Delivery), depending on the project's needs and the team's comfort level with automatic deployments.

This workflow emphasizes automation, testing, and code review, ensuring that new features and fixes are thoroughly vetted before reaching end-users, thereby maintaining the quality and stability of the application.



# Regression ELI5
Imagine you're building a tower with blocks, and every day you add a few more blocks to make it taller. But one day, after adding new blocks, you notice that a part of the tower you built last week has fallen down. In the software world, we call this a "regression."

In software testing, "regression" means that something that used to work fine before isn't working now, even though you didn't mean to change it. It's like when you add a new piece to your tower, and it accidentally knocks over something else that was already there.

We do "regression testing" to make sure that when we add new things to our software (like new features or bug fixes), we don't accidentally break something that was already working well. It's like checking all the parts of your tower every time you add new blocks, just to make sure everything is still standing strong.












# Staging environment git setup
When using Heroku and you have created a separate staging app, you don't necessarily set the Git remote for a specific branch (like your staging branch) to this app. Instead, you manage the deployment to different Heroku apps (staging and production) by setting up separate Git remotes for each Heroku app. Here's how to do it:

### 1. Verify Existing Remotes

First, check your existing Git remotes to understand the current configuration. Open your terminal, navigate to your project directory, and run:

```bash
git remote -v
```

You'll likely see the remote for your production app, typically named `origin` for your code repository and possibly `heroku` for your Heroku production app.

### 2. Add a Remote for the Staging App

You'll add a new remote for your Heroku staging app. Heroku CLI provides an easy way to add a remote associated with a Heroku app. Use the following command:

```bash
heroku git:remote -a your-staging-app-name -r staging
```

Replace `your-staging-app-name` with the name of your Heroku staging app. The `-r staging` option sets the name of the remote to `staging`. After running this command, `staging` will be the name of the remote pointing to your Heroku staging app.

### 3. Deploy to Staging

To deploy code to your staging app, you just need to push the desired branch (e.g., your `staging` branch) to the `staging` remote. Here's how you do it:

```bash
git push staging staging:main
```

This command pushes the `staging` branch from your local repository to the `main` branch on the `staging` remote (Heroku automatically deploys the `main` branch by default). If your Heroku app is set to deploy from a different branch, replace `main` with the name of that branch.

### 4. Managing Config Vars

Remember to set environment variables (config vars in Heroku) for your staging app separately from your production app. You can do this through the Heroku dashboard or the CLI:

```bash
heroku config:set VAR_NAME=value -a your-staging-app-name
```

Replace `VAR_NAME=value` with your actual configuration variables and their values.

### Summary

By setting up a separate remote for your staging app on Heroku, you can easily manage deployments to staging and production independently. This setup allows you to maintain a stable production environment while testing new features and changes in staging.
