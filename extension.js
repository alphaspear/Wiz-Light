const GETTEXT_DOMAIN = 'my-indicator-extension';

const { GObject, St } = imports.gi;

const Gettext = imports.gettext.domain(GETTEXT_DOMAIN);
const _ = Gettext.gettext;
const Util = imports.misc.util;
const ExtensionUtils = imports.misc.extensionUtils;
const Main = imports.ui.main;
const PanelMenu = imports.ui.panelMenu;
const PopupMenu = imports.ui.popupMenu;

const Indicator = GObject.registerClass(
class Indicator extends PanelMenu.Button {
    _init() {
        super._init(0.0, _('My Shiny Indicator'));

        let box = new St.BoxLayout({ style_class: 'panel-status-menu-box' });
        box.add_child(new St.Icon({
            icon_name: 'face-smile-symbolic',
            style_class: 'system-status-icon',
        }));
        box.add_child(PopupMenu.arrowIcon(St.Side.BOTTOM));
        this.add_child(box);

        let item = new PopupMenu.PopupMenuItem(_('Lights On'));
        item.connect('activate', () => {
            Util.spawn(["python3",".local/share/gnome-shell/extensions/wizlight@iabhilashjoshi@gmail.com/on.py"]);
            Main.notify(_('Power On Signal Sent'));
        });
        
        let item2 = new PopupMenu.PopupMenuItem(_('Lights Off'));
        item2.connect('activate', () => {
            Util.spawn(["python3",".local/share/gnome-shell/extensions/wizlight@iabhilashjoshi@gmail.com/off.py"]);
            Main.notify(_('Power Off Signal Sent'));
        });
        this.menu.addMenuItem(item);
        this.menu.addMenuItem(item2);
    }
});

class Extension {
    constructor(uuid) {
        this._uuid = uuid;

        ExtensionUtils.initTranslations(GETTEXT_DOMAIN);
    }

    enable() {
        this._indicator = new Indicator();
        Main.panel.addToStatusArea(this._uuid, this._indicator);
    }

    disable() {
        this._indicator.destroy();
        this._indicator = null;
    }
}

function init(meta) {
    return new Extension(meta.uuid);
}
