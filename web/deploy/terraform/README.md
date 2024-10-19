# Resource Deployment

## General Notes

Deployment of infrastructure resources requires [OpenTofu](https://opentofu.org/) (version >=1.8.0).

When calling modules, the relevant input variables can be found in their `variables.tf` file or sometimes their `variables_state.tf` file. This is where the parametrization takes place. In general, a module's `main.tf` file should only be modified if you would like to change what infrastructure is created. Modifying a module's `main.tf` file should seldom be necessary. 

## Deployment Steps

### 0. Bootstrap Step: Deploy State Resources

> **_Note:_** This step should be run manually on the developer's/infrastructure engineer's local machine. All subsequent steps will be run automatically by a CD workflow.

> **_Note:_** This step should only be run once for the lifetime of the deployment. 

It is recommended that you use the default variable values, as defined in `modules/state/variables.tf`. If you want to change the values from the defaults, you can add your desired values in `state/main.tf`. You will then need to change the corresponding values in the `variables_state.tf` files of the resources (i.e. `shared`, `staging`, and `production`) to match what you set in `state/main.tf`. This can be done in an automated way by running 

```bash
$ cd ~/path-to-repo/web/deploy/terraform/
$ # Change DynamoDB state lock table names
$ find staging/ shared/ production/ -name "variables_state.tf" -exec sed -i "s/terraform-state-locks/foo-bar-state-locks/g" {} +
$ # Change names of S3 buckets that store OpenTofu state
$ find staging/ shared/ production/ -name "variables_state.tf" -exec sed -i "s/osm-terraform-state-storage/foo-bar-state-storage-test/g" {} +
$ # Change AWS region where state resources reside
$ find staging/ shared/ production/ -name "variables_state.tf" -exec sed -i "s/us-east-1/us-foobar-1/g" {} +
```

Once you have configured the variables (or preferably will be using the defaults), you can deploy the state management resources with 

```bash
$ cd ~/path-to-repo/web/deploy/terraform/state/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

> **_NOTE:_** In order to prevent accidental destruction, the `state` modules are configured to [prevent destruction](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle#prevent_destroy) ([more info on `prevent_destroy`](https://developer.hashicorp.com/terraform/tutorials/state/resource-lifecycle#prevent-resource-deletion)) using OpenTofu. To destroy state resources, you must do so manually in the AWS Management Console. 

### 1. Deploy Shared Resources

> **_Note:_** This step will usually be run by a CD workflow. This step is included here for development/debugging purposes.

First, for each resource defined by a module in `shared/main.tf`, make sure that resource's input variables are set to your desired values. You can find the input variables for a module `foo` in `modules/foo/variables.tf`.

Then you can deploy the shared resources with 

```bash
$ cd ~/path-to-repo/web/deploy/terraform/shared/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

### 2. Deploy Staging Resources

> **_Note:_** This step will usually be run by a CD workflow. This step is included here for development/debugging purposes.

First, for each resource defined by a module in `staging/main.tf`, make sure that resource's input variables are set to your desired values. You can find the input variables for a module `foo` in `modules/foo/variables.tf`.

Then you can deploy the staging resources with 

```bash
$ cd ~/path-to-repo/web/deploy/terraform/staging/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

### 3. Deploy Production Resources

> **_Note:_** This step will usually be run by a CD workflow. This step is included here for development/debugging purposes.

First, for each resource defined by a module in `production/main.tf`, make sure that resource's input variables are set to your desired values. You can find the input variables for a module `foo` in `modules/foo/variables.tf`.

Then you can deploy the production resources with 

```bash
$ cd ~/path-to-repo/web/deploy/terraform/production/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```
