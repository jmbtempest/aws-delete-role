#! /usr/bin/env python

"""Module providing a function to delete AWS role."""

import boto3

def delete_iam_role(target_role_name):
    """Function delete AWS Role."""
    # Using awslogin and assume role to get the credentials
    # Read available AWS profiles from a file
    # Ensure the file 'available_profiles.txt' exists and contains valid AWS profile names
    # Profile names should be listed one per line
    # Profile names should match AWS Account names
    with open('available_profiles.txt', 'r', encoding="utf-8",) as file:
        available_profiles = [line.strip() for line in file.readlines()]
        print(f"{available_profiles}")

    for profile in available_profiles:
        aws_session = boto3.session.Session(profile_name=profile)

        try:
            iam = aws_session.client('iam')

            # Detach all attached managed policies
            attached_policies = iam.list_attached_role_policies(
                RoleName=target_role_name)['AttachedPolicies']
            for policy in attached_policies:
                print(
                    f"Detaching managed policy: {policy['PolicyName']} "
                    f"from role: {target_role_name}"
                )
                iam.detach_role_policy(RoleName=target_role_name, PolicyArn=policy['PolicyArn'])

            # Delete inline policies
            inline_policies = iam.list_role_policies(RoleName=target_role_name)['PolicyNames']
            for policy_name in inline_policies:
                print(f"Deleting inline policy: {policy_name} from role: {target_role_name}")
                iam.delete_role_policy(RoleName=target_role_name, PolicyName=policy_name)

            # Remove the role from any associated instance profiles
            instance_profiles = iam.list_instance_profiles_for_role(
                RoleName=target_role_name)['InstanceProfiles']
            for instance_profile in instance_profiles:
                print(
                    f"Removing role: {target_role_name} "
                    f"from instance profile: {instance_profile['InstanceProfileName']}"
                )
                iam.remove_role_from_instance_profile(
                    InstanceProfileName=instance_profile['InstanceProfileName'],
                    RoleName=target_role_name
                )
                iam.delete_instance_profile(InstanceProfileName=instance_profile
                    ['InstanceProfileName']
                )

            ## Delete IAM role
            print(f"Deleting IAM role: {target_role_name}")
            iam.delete_role(RoleName=target_role_name)
            print(f"Successfully deleted IAM role: '{target_role_name}' in account '{profile}'.")

        except iam.exceptions.NoSuchEntityException:
            print(f"IAM role '{target_role_name}' not found in account '{profile}'.")
        except Exception as e:
            print(f"Error deleting IAM role '{target_role_name}' in account '{profile}'.': {e}")

if __name__ == "__main__":
    while True:
        #target_role_name = "borsch-test-role"
        target_role_name = input("Enter the IAM role name to delete: ")

        # Input validation
        if isinstance(target_role_name, str):
            # Confirmation step
            confirm = input(f"You entered '{target_role_name}'. Is this correct? (Y/N): ").lower()

            if confirm in ('y', 'yes'):
                print("Group name confirmed.")
                # Proceed with the rest of your program
                break  # Exit the loop if confirmed
            elif confirm in ('n', 'no'):
                print("Please re-enter the group name.")
                continue  # Continue the loop to ask for input again
            else:
                print("Invalid input. Please enter 'Y' or 'N'.")
                continue  # Continue the loop

        else:
            print("Invalid group name.")

    delete_iam_role(target_role_name)
