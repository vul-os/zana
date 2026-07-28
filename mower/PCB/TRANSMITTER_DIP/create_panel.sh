#!/usr/bin/env bash
# Panelise the thru-hole TRANSMITTER board 4x4 for home fabrication.
# Requires KiKit: https://github.com/yaqwsx/KiKit
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

kikit panelize \
    --layout 'hspace: 1mm; vspace: 0.5mm; rows: 4; cols: 4' \
    "$here/TRANSMITTER.kicad_pcb" "$here/TRANSMITTER_PANEL.kicad_pcb"
