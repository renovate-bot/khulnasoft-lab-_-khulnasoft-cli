import sys
import json
import click

import khulnasoftcli.clients.apiexternal

config = {}


@click.group(name="subscription", short_help="Subscription operations")
@click.pass_obj
def subscription(ctx_config):
    global config
    config = ctx_config

    try:
        khulnasoftcli.cli.utils.check_access(config)
    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "subscription", {}, err))
        sys.exit(2)


@subscription.command(name="activate", short_help="Activate a subscription")
@click.argument("subscription_type", nargs=1, required=True)
@click.argument("subscription_key", nargs=1, required=True)
def activate(subscription_type, subscription_key):
    """
    SUBSCRIPTION_TYPE: Type of subscription. Valid options:

      - tag_update: Receive notification when new image is pushed

      - policy_eval: Receive notification when image policy status changes

      - vuln_update: Receive notification when vulnerabilities are added, removed or modified

    SUBSCRIPTION_KEY: Fully qualified name of tag to subscribe to. Eg. docker.io/library/alpine:latest
    """
    ecode = 0

    try:
        ret = khulnasoftcli.clients.apiexternal.activate_subscription(
            config, subscription_type, subscription_key
        )
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "subscription_activate", {}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(
                config, "subscription_activate", {}, err
            )
        )
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@subscription.command(name="deactivate", short_help="Deactivate a subscription")
@click.argument("subscription_type", nargs=1, required=True)
@click.argument("subscription_key", nargs=1, required=True)
def deactivate(subscription_type, subscription_key):
    """
    SUBSCRIPTION_TYPE: Type of subscription. Valid options:

      - tag_update: Receive notification when new image is pushed

      - policy_eval: Receive notification when image policy status changes

      - vuln_update: Receive notification when vulnerabilities are added, removed or modified

    SUBSCRIPTION_KEY: Fully qualified name of tag to subscribe to. Eg. docker.io/library/alpine:latest
    """
    ecode = 0

    try:
        ret = khulnasoftcli.clients.apiexternal.deactivate_subscription(
            config, subscription_type, subscription_key
        )
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "subscription_deactivate", {}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(
                config, "subscription_deactivate", {}, err
            )
        )
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@subscription.command(name="list", short_help="List all current subscriptions")
@click.option(
    "--full",
    is_flag=True,
    help="Print additional details about the subscriptions as they're being listed",
)
def list_subscriptions(full):
    ecode = 0
    try:
        ret = khulnasoftcli.clients.apiexternal.get_subscription(config)
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "subscription_list", {"full": full}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(
                config, "subscription_list", {}, err
            )
        )
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@subscription.command(
    name="get", short_help="Get details about a particular subscription"
)
@click.argument("subscription_id", nargs=1, required=True)
def get_subscription_by_id(subscription_id):
    return_code = 0
    try:
        ret = khulnasoftcli.clients.apiexternal.get_subscription_by_id(
            config, subscription_id
        )
        return_code = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "subscription_get", {"full": True}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))
    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(
                config, "subscription_get", {}, err
            )
        )
        if not return_code:
            return_code = 2

    khulnasoftcli.cli.utils.doexit(return_code)


@subscription.command(
    name="del", short_help="Delete a subscription by ID (must be already deactivated)"
)
@click.argument("subscription_id", nargs=1, required=True)
def delete_subscription_by_id(subscription_id):
    return_code = 0
    try:
        ret = khulnasoftcli.clients.apiexternal.delete_subscription_by_id(
            config, subscription_id
        )
        return_code = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print("Success")
        else:
            raise Exception(json.dumps(ret["error"], indent=4))
    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(
                config, "subscription_delete", {}, err
            )
        )
        if not return_code:
            return_code = 2

    khulnasoftcli.cli.utils.doexit(return_code)
