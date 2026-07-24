from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class LoaMenuItem(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(
            self,
            "Leave of Absence",
            "fas fa-plane-departure fa-fw",
            "aa_loa:index",
            navactive=["aa_loa:"],
        )

    def render(self, request):
        if request.user.has_perm("aa_loa.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return LoaMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "aa_loa", r"^loa/")
