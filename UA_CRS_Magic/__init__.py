def classFactory(iface):  # pylint: disable=invalid-name
    from .code import CRS_Magic
    return CRS_Magic(iface)
