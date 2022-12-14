///////////////////////////////////////////////////////////////////////////////
//Enter Your Bulb's IP address below in order to control the bulb/////////////
/////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
const ipaddress = "192.168.29.189";////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
const Main = imports.ui.main;
const Gio = imports.gi.Gio;
const PanelMenu = imports.ui.panelMenu;
const PopupMenu = imports.ui.popupMenu;
const Me = imports.misc.extensionUtils.getCurrentExtension();

//
const GETTEXT_DOMAIN = 'my-indicator-extension';

const { GObject, St } = imports.gi;

const Gettext = imports.gettext.domain(GETTEXT_DOMAIN);
const _ = Gettext.gettext;
const Util = imports.misc.util;
const ExtensionUtils = imports.misc.extensionUtils;

const BASE_PATH = Me.dir.get_path();

//

let myPopup;

const MyPopup = GObject.registerClass(
class MyPopup extends PanelMenu.Button {

  _init () {
  
    super._init(0);
    
    let icon = new St.Icon({
      icon_name : 'emoji-objects-symbolic',
      //gicon : Gio.icon_new_for_string( BASE_PATH + '/icon.svg' ),
      style_class : 'system-status-icon',
    });
    
    this.add_child(icon);
    
    

    this.menu.connect('open-state-changed', (menu, open) => {
      if (open) {
        log('opened');
      } else {
        log('closed');
      }
    });
    
    ///////////power control start//////////
    let power_switch = new PopupMenu.PopupSubMenuMenuItem('Set State');
    this.menu.addMenuItem(power_switch);
    
    let item_on = new PopupMenu.PopupMenuItem('Power On');
    power_switch.menu.addMenuItem( item_on ,0);
    item_on.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/state.py", ipaddress, "on"]);
        Main.notify(_('Lights Up!!'));
    });

    let item_off = new PopupMenu.PopupMenuItem('Power Off');
    power_switch.menu.addMenuItem( item_off ,1);
    item_off.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/state.py", ipaddress, "off"]);
        Main.notify(_('Lights Down!!'));
    });
    ///////////power control end//////////


///////////brightness control start//////////
    let brightness_switch = new PopupMenu.PopupSubMenuMenuItem('Brightness');
    this.menu.addMenuItem(brightness_switch);
    
    let item_brightness_25 = new PopupMenu.PopupMenuItem('25%');
    brightness_switch.menu.addMenuItem( item_brightness_25 ,0);
    item_brightness_25.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/brightness.py", ipaddress, "25"]);
        Main.notify(_('Brightness Set To 25%'));
    });

    let item_brightness_50 = new PopupMenu.PopupMenuItem('50%');
    brightness_switch.menu.addMenuItem( item_brightness_50 ,1);
    item_brightness_50.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/brightness.py", ipaddress, "50"]);
        Main.notify(_('Brightness Set To 50%'));
    });

    let item_brightness_75 = new PopupMenu.PopupMenuItem('75%');
    brightness_switch.menu.addMenuItem( item_brightness_75 ,2);
    item_brightness_75.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/brightness.py", ipaddress, "75"]);
        Main.notify(_('Brightness Set To 75%'));
    });

    let item_brightness_100 = new PopupMenu.PopupMenuItem('100%');
    brightness_switch.menu.addMenuItem( item_brightness_100 ,3);
    item_brightness_100.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/brightness.py", ipaddress, "100"]);
        Main.notify(_('Brightness Set To 100%'));
    });
///////////brightness control end//////////

//////////////color control ////start///////////
    let color_switch = new PopupMenu.PopupSubMenuMenuItem('Colors');
    this.menu.addMenuItem(color_switch);
    
    let item_color_white = new PopupMenu.PopupMenuItem('Cool White');
    color_switch.menu.addMenuItem( item_color_white ,0);
    item_color_white.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/color.py", ipaddress, "coolwhite"]);
        Main.notify(_('Color Changed To Cool White'));
    });

    let item_color_Warmwhite = new PopupMenu.PopupMenuItem('Warm White');
    color_switch.menu.addMenuItem( item_color_Warmwhite ,1);
    item_color_Warmwhite.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/color.py", ipaddress, "warmwhite"]);
        Main.notify(_('Color Changed To Warm White'));
    });
    
    let item_color_red = new PopupMenu.PopupMenuItem('Red');
    color_switch.menu.addMenuItem( item_color_red ,2);
    item_color_red.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/color.py", ipaddress, "red"]);
        Main.notify(_('Going Red'));
    });
    
    
    let item_color_blue = new PopupMenu.PopupMenuItem('Blue');
    color_switch.menu.addMenuItem( item_color_blue ,3);
    item_color_blue.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/color.py", ipaddress, "blue"]);
        Main.notify(_('Going Blue'));
    });

    let item_color_green = new PopupMenu.PopupMenuItem('Green');
    color_switch.menu.addMenuItem( item_color_green ,4);
    item_color_green.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/color.py", ipaddress, "green"]);
        Main.notify(_('Going Green'));
    });
    ///////////color control /////end

    ///////////scene control /////start
    let scene_switch = new PopupMenu.PopupSubMenuMenuItem('Scene');
    this.menu.addMenuItem(scene_switch);
    
    let item_scene_party = new PopupMenu.PopupMenuItem('Party');
    scene_switch.menu.addMenuItem( item_scene_party ,0);
    item_scene_party.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/scene.py", ipaddress, "4"]);
        Main.notify(_('Party Hard'));
    });

    let item_scene_fireplace = new PopupMenu.PopupMenuItem('Fireplace');
    scene_switch.menu.addMenuItem( item_scene_fireplace ,1);
    item_scene_fireplace.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/scene.py", ipaddress, "5"]);
        Main.notify(_('Fireing it up!!'));
    });

    let item_scene_tvtime = new PopupMenu.PopupMenuItem('TV Time');
    scene_switch.menu.addMenuItem( item_scene_tvtime ,2);
    item_scene_tvtime.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/scene.py", ipaddress, "18"]);
        Main.notify(_('TV Time!!'));
    });

    let item_scene_deepdive = new PopupMenu.PopupMenuItem('Deepdive');
    scene_switch.menu.addMenuItem( item_scene_deepdive ,3);
    item_scene_deepdive.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/scene.py", ipaddress, "23"]);
        Main.notify(_('Going deep waters!!'));
    });

    let item_scene_christmas = new PopupMenu.PopupMenuItem('Christmas');
    scene_switch.menu.addMenuItem( item_scene_christmas ,4);
    item_scene_christmas.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/scene.py", ipaddress, "27"]);
        Main.notify(_('Merry Christmas'));
    });

    let item_scene_halloween = new PopupMenu.PopupMenuItem('Halloween');
    scene_switch.menu.addMenuItem( item_scene_halloween ,5);
    item_scene_halloween.connect('activate', () => {
        Util.spawn(["python3", BASE_PATH + "/scene.py", ipaddress, "28"]);
        Main.notify(_('Happy Halloween'));
    });
    ///////////scene control /////end

    
    ///////////speed control /////start
    ///////////speed control /////end


  }

});

function init() {
}

function enable() {
  myPopup = new MyPopup();
  Main.panel.addToStatusArea('myPopup', myPopup, 1);
}

function disable() {
  myPopup.destroy();
}

