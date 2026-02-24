python3 -m venv .venv
. .venv/bin/activate
pip install fake-bpy-module-3.2
ln -s -t ~/.config/blender/4.2/scripts/addons/ $(realpath .)
