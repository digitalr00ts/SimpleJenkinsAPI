"""Inspired by the Jenkins CLI.
These commands are experimental.
"""
import functools

from SimpleJenkinsAPI.main import SimpleJenkinsAPIs


# fmt: off
def ensure_client(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        simplejenkins = kwargs.get("simplejenkins")
        if not args and not simplejenkins:
            simplejenkins = kwargs["simplejenkins"] = SimpleJenkinsAPIs()
        else:
            simplejenkins = args[0]
        is_client = bool(simplejenkins.client())

        try:
            if not is_client: simplejenkins.open_client()
            value = func(*args, **kwargs)
        finally:
            if not is_client: simplejenkins.close()

        return value

    return wrapper
# fmt: on


@ensure_client
def list_masters(simplejenkins: SimpleJenkinsAPIs):
    rtn = simplejenkins.api(
        "view/Masters",
        depth=1,
        tree="jobs[name,displayName,fullName,description,online,approved,url,endpoint]",
    )
    return rtn["jobs"]


# https://docs.cloudbees.com/docs/admin-resources/latest/cli-guide/casc-bundle-management
# https://docs.cloudbees.com/docs/cloudbees-ci-api/latest/bundle-management-api
@ensure_client
def casc_bundle_list(simplejenkins: SimpleJenkinsAPIs):
    return simplejenkins.casc("list")


@ensure_client
def casc_bundle_set_master(
    simplejenkins: SimpleJenkinsAPIs,
    bundle_id: str = None,
    master_path: str = None,
):

    return simplejenkins.casc(
        "set-master-to-bundle", data={"bundleId": bundle_id, "masterPath": master_path}
    )
