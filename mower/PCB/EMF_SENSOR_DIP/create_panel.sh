#!/usr/bin/env bash
# Panelise the thru-hole EMF_SENSOR board 4x6 for home fabrication.
# Requires KiKit: https://github.com/yaqwsx/KiKit
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

kikit panelize \
    --layout 'hspace: 1mm; vspace: 1mm; rows: 4; cols: 6' \
    "$here/EMF_SENSOR.kicad_pcb" "$here/EMF_SENSOR_PANEL.kicad_pcb"
