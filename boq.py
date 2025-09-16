import streamlit as st
import pandas as pd
import io
import re
from typing import Dict, List, Tuple
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Optional Gemini (Google Generative) import
try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# Hardcoded Gemini API Key
GEMINI_API_KEY = "AIzaSyBT5J7ZvT00QBsQDGIk9GNx03-QKmp0Bm4"
BOQ_TEMPLATE ={
    "1. Preliminaries": {
        "keywords": ["management", "staff", "accommodation", "temporary", "establishment", "survey", "testing", "commissioning", "handover", "scaffolding", "records", "cleaning", "insurance", "protection"],
        "items": [
            "Project specific management and staff",
            "Staff travel",
            "Site accommodation",
            "Temporary works in connection with site establishment",
            "Furniture and equipment",
            "IT systems",
            "Consumables and services",
            "Sundries",
            "Temporary water supply",
            "Temporary gas supply",
            "Temporary electricity supply",
            "Temporary telecommunication system",
            "Survey, inspections and monitoring",
            "Setting out",
            "Protection of Works",
            "Samples",
            "Environmental control of building",
            "Mechanical plant",
            "Access scaffolding",
            "Temporary works",
            "Site records",
            "Testing and commissioning plan",
            "Handover",
            "Post-completion services",
            "Site tidy",
            "Charges",
            "Insurances"
        ]
    },
    "2. Offsite manufactured material, components or buildings": {
        "keywords": ["component", "prefabricated", "structures", "building", "units", "manufactured", "offsite"],
        "items": [
            "Component",
            "Prefabricated structures",
            "Prefabricated building units",
            "Prefabricated buildings"
        ]
    },
    "3. Demolitions": {
        "keywords": ["demolitions", "temporary", "support", "decontamination", "recycling", "structures", "roads"],
        "items": [
            "Demolitions",
            "Temporary support of structures, roads and the like",
            "Temporary works",
            "Decontamination",
            "Recycling"
        ]
    },
    "4. Alterations, repairs and conservation": {
        "keywords": ["alteration", "removing", "cutting", "opening", "recess", "filling", "replacing", "repairing", "repointing", "cleaning", "conservation", "renovation", "weathering"],
        "items": [
            "Works of alteration",
            "Removing",
            "Cutting or forming openings",
            "Cutting or forming recesses",
            "Cutting back",
            "Filling in openings",
            "Filling in recesses",
            "Removing existing and replacing",
            "Preparing existing structures for connection or attachment of new work",
            "Repairing",
            "Repointing joints",
            "Repointing",
            "Resin or cement impregnation/injection",
            "Inserting new walls ties",
            "Re-dressing existing flashings and the like",
            "Damp-proof course renewal",
            "Damp-proof course insertion",
            "Cleaning surfaces",
            "Removing stains",
            "Artificial weathering",
            "Renovating",
            "Conserving",
            "Decontamination",
            "Temporary works Roads",
            "Recycling"
        ]
    },
    "5. Excavation and filling": {
        "keywords": ["excavation", "filling", "trees", "clearance", "preparation", "disposal", "retaining", "imported", "geotextile", "membrane", "barrier", "stabilisation"],
        "items": [
            "Preliminary sitework",
            "Removing trees",
            "Removing tree stumps",
            "Site clearance",
            "Site preparation",
            "Excavation, commencing level stated if not original ground level",
            "Extra over all types of excavation irrespective of depth",
            "Support to face(s) of excavation where not at the discretion of the contractor",
            "Disposal",
            "Retaining excavated material on site",
            "Filling obtained from excavated material",
            "Imported filling",
            "Geotextile fabric",
            "Radon barrier",
            "Methane barrier",
            "Damp proof membrane",
            "Ground movement protection boards",
            "Ground stabilisation meshes and the like, type stated",
            "Cutting off tops of piles irrespective of length"
        ]
    },
    "6. Ground remediation and soil stabilisation": {
        "keywords": ["dewatering", "sterilisation", "neutralising", "freezing", "venting", "nailing", "anchors", "grouting", "compacting", "stabilising"],
        "items": [
            "Site dewatering",
            "Sterilisation",
            "Chemical neutralising",
            "Freezing",
            "Ground gas venting",
            "Soil nailing",
            "Ground anchors",
            "Pressure grouting/ground permeation",
            "Compacting",
            "Stabilising soil in situ by incorporating cement with a rotavator"
        ]
    },
    "7. Piling": {
        "keywords": ["piles", "interlocking", "bored", "driven", "vibro-compacted", "reinforcement", "testing", "disposal", "obstructions"],
        "items": [
            "Interlocking sheet piles",
            "Bored piles",
            "Driven piles",
            "Other type piles",
            "Vibro-compacted piles",
            "vibro-compacted trench fill",
            "Extra over piling",
            "Reinforcement to in-situ concrete piles",
            "Breaking through obstructions",
            "Disposal of excavated materials",
            "Delays",
            "Tests"
        ]
    },
    "8. Underpinning": {
        "keywords": ["underpinning", "concrete", "formwork", "reinforcement", "brickwork", "blockwork", "tanking"],
        "items": [
            "Underpinning",
            "Concrete",
            "Formwork",
            "Reinforcement",
            "Brickwork or blockwork",
            "Tanking"
        ]
    },
    "9. Diaphragm walls and embedded retaining walls": {
        "keywords": ["walls", "thickness", "excavation", "disposal", "joints", "trimming", "cleaning", "delays", "tests"],
        "items": [
            "Walls, thickness stated",
            "Extra over excavation and disposal",
            "Joints",
            "Trimming and cleaning exposed faces",
            "Delays",
            "Tests"
        ]
    },
    "10. Crib walls, gabions and reinforced earth": {
        "keywords": ["crib", "walls", "gabion", "basket", "earth", "reinforcement"],
        "items": [
            "Crib walls",
            "Extra for",
            "Gabion basket walls",
            "Earth reinforcement"
        ]
    },
    "11. Insitu concrete works": {
        "keywords": ["concrete", "mass", "horizontal", "vertical", "sprayed", "formwork", "reinforcement", "joints", "grouting", "trowelling", "floating"],
        "items": [
            "Mass concrete",
            "Horizontal work",
            "Vertical work",
            "Sundry in-situ concrete work",
            "Sprayed in-situ concrete",
            "Trowelling",
            "Power floating",
            "Hacking",
            "Grinding",
            "Sides of foundations and bases",
            "Edges of horizontal work",
            "Soffits of horizontal work",
            "Sides and soffits of isolated beams",
            "Sides and soffits of attached beams",
            "Sides of upstand beams",
            "Sides of attached columns",
            "Faces of walls and other vertical work",
            "Staircase strings and the like",
            "Staircase risers and the like",
            "Complex shapes",
            "Wall kickers",
            "Reinforcement",
            "Mild steel bars",
            "High yield steel bars",
            "Pre/Post-tensioned members",
            "Mesh",
            "Plain joints",
            "Formed joints",
            "Cut joints",
            "Grouting",
            "Filling mortices or holes",
            "Filling chases"
        ]
    },
    "12. Precast/composite concrete": {
        "keywords": ["composite", "concrete", "designed", "joints", "holding", "tie", "straps"],
        "items": [
            "Composite concrete work",
            "Designed joints",
            "Holding down or tie straps"
        ]
    },
    "13. Precast concrete": {
        "keywords": ["precast", "concrete", "goods", "rooflights", "pavement", "lights", "vertical", "panel", "joints"],
        "items": [
            "Precast concrete goods",
            "Rooflights",
            "Pavement lights",
            "Vertical panel lights",
            "Designed joints",
            "Holding down or tie straps"
        ]
    },
    "14. Masonry": {
        "keywords": ["walls", "thickness", "diaphragm", "vaulting", "piers", "arches", "bands", "flues", "cavity", "insulation", "damp-proof", "pointing"],
        "items": [
            "Walls; overall thickness stated",
            "Diaphragm walls; overall thickness stated, spacing and thickness of ribs stated",
            "Vaulting; thickness and type stated",
            "Isolated piers; isolated casings; chimney stacks; columns",
            "Attached projections",
            "Arches (number stated)",
            "Bands; dimensioned description",
            "Flues",
            "Flue linings",
            "Filling around flues",
            "Extra over walls for perimeters and abutments, details stated",
            "Extra over walls for opening perimeters, details stated",
            "Special purpose blocks or stones",
            "Forming cavity",
            "Cavity insulation",
            "Damp-proof courses < 300mm wide",
            "Damp-proof courses > 300mm wide",
            "Pre-formed cavity trays",
            "Joint reinforcement",
            "Fillets",
            "Pointing",
            "Joints",
            "Wedging and pinning",
            "Creasing",
            "Proprietary and individual spot items"
        ]
    },
    "15. Structural metalwork": {
        "keywords": ["framed", "members", "fabrication", "erection", "isolated", "structural", "purlins", "cladding", "decking", "bolts", "connections", "coatings"],
        "items": [
            "Framed members, framing and fabrication",
            "Framed members, permanent erection on site",
            "Isolated structural members, fabrication",
            "Isolated structural members, permanent erection on site",
            "Allowance for fittings",
            "Cold rolled purlins, cladding rails and the like",
            "Extra over for",
            "Profiled metal decking, type and/or profile stated",
            "Holding down bolts or assemblies",
            "Special bolts",
            "Connections to existing steel and other members or structures",
            "Trial erection",
            "Filling hollow sections",
            "Surface treatments",
            "Isolated protective coatings",
            "Testing"
        ]
    },
    "16. Carpentry": {
        "keywords": ["primary", "structural", "timbers", "engineered", "prefabricated", "backing", "boarding", "flooring", "sheeting", "decking", "fascias", "soffits", "fixings"],
        "items": [
            "Primary or structural timbers",
            "Engineered or prefabricated members/items",
            "Backing and other first fix timbers",
            "Boarding, flooring, sheeting, decking, casings, linings, sarking, fascias, bargeboards, soffits and the like",
            "Ornamental ends of timber members",
            "Metal fixings, fastenings and fittings"
        ]
    },
    "17. Sheet roof covering": {
        "keywords": ["coverings", "boundary", "flashings", "gutters", "valleys", "spot", "items", "fittings", "forming"],
        "items": [
            "Coverings > 500mm wide",
            "Coverings < 500mm wide",
            "Extra over for forming",
            "Boundary work, location and method of forming described",
            "Flashings",
            "Gutters",
            "Valleys",
            "Spot items",
            "Fittings"
        ]
    },
    "18. Tile and slate roof and wall covering": {
        "keywords": ["roof", "coverings", "wall", "coverings", "boundary", "fittings", "tile", "slate"],
        "items": [
            "Roof coverings",
            "Wall coverings",
            "Boundary work; location and method of forming described",
            "Fittings"
        ]
    },
    "19. Water proofing": {
        "keywords": ["coverings", "skirtings", "fascias", "aprons", "gutters", "channels", "valleys", "kerbs", "spot", "items", "fittings", "trim"],
        "items": [
            "Coverings > 500mm wide",
            "Coverings < 500mm wide",
            "Skirtings",
            "Fascias",
            "Aprons",
            "Gutters",
            "Channels",
            "Valleys",
            "Kerbs",
            "Spot items",
            "Fittings",
            "Edge trim"
        ]
    },
    "20. Proprietary linings and partitions": {
        "keywords": ["proprietary", "metal", "framed", "system", "walls", "ceilings", "openings", "perimeter", "angles", "junctions", "access", "panels", "linings"],
        "items": [
            "Proprietary metal framed system to form walls",
            "Proprietary metal framed system to form ceilings",
            "Extra over for different",
            "Extra over for forming openings",
            "Extra over for non-standard perimeter details",
            "Extra over for angles",
            "Extra over for junctions",
            "Extra over for access panels",
            "Fair ends to partitions",
            "Proprietary linings to walls",
            "Proprietary linings to ceilings",
            "Proprietary linings to columns",
            "Proprietary linings to beams",
            "Proprietary linings to bulkheads",
            "Beads, function stated"
        ]
    },
    "21. Cladding and coverings": {
        "keywords": ["walls", "floors", "ceilings", "roofs", "dormers", "beams", "columns", "boundary", "opening", "perimeters", "angles", "closers"],
        "items": [
            "Walls",
            "Floors",
            "Ceilings",
            "Roofs",
            "Sides and tops of dormers",
            "Sides and soffits of beams",
            "Sides of columns",
            "Items extra over the work in which they occur",
            "Boundary work",
            "Opening perimeters",
            "Angles",
            "Closers"
        ]
    },
    "22. General joinery": {
        "keywords": ["skirtings", "architraves", "cover", "fillets", "stops", "trims", "beads", "nosings", "shelves", "worktops", "window", "boards", "handrails", "casings", "boarding", "partitions", "ironmongery"],
        "items": [
            "Skirtings, picture rails",
            "Architraves and the like",
            "Cover fillets, stops, trims, beads, nosings and the like",
            "Isolated shelves and worktops",
            "Window boards",
            "Isolated handrails and grab rails",
            "Duct covers",
            "Pipe casings",
            "Shelves",
            "Pinboards, backboards, plinth blocks and the like Floor, wall and ceiling boarding, sheeting, panelling, linings and casings",
            "Boarding, sheeting, panelling over 600mm wide",
            "Boarding, sheeting, panelling not exceeding 600mm wide",
            "Partitions",
            "Items extra over the partition they occur in",
            "Duct panels, Sanitary ware back panels and the like",
            "Cubicle partition sets",
            "Infill panels and sheets, number stated",
            "Joints: contact surfaces stated",
            "Pointing: contact surfaces stated",
            "Raking out existing joints",
            "Type of item, unit or set stated"
        ]
    },
    "23. Windows, screens and lights": {
        "keywords": ["windows", "frames", "shutters", "sun", "shields", "rooflights", "skylights", "screens", "borrowed", "lights", "shop", "fronts", "louvres", "glazing", "ironmongery"],
        "items": [
            "Windows and window frames",
            "Window shutters",
            "Sun shields",
            "Rooflights, skylights and lanternlights",
            "Screens, borrowed lights and frames",
            "Shop fronts",
            "Louvres and frames",
            "Glazing",
            "Glass, type stated",
            "Louvre blades",
            "Ironmongery",
            "Type of item, unit or set stated"
        ]
    },
    "24. Doors, shutters and hatches": {
        "keywords": ["door", "sets", "doors", "roller", "shutters", "collapsible", "gates", "sliding", "folding", "partitions", "hatches", "strong", "room", "grilles", "frames", "linings", "stops", "glazing", "ironmongery"],
        "items": [
            "Door sets",
            "Doors",
            "Roller shutters",
            "Collapsible gates",
            "Sliding folding partitions",
            "Hatches",
            "Strong room doors",
            "Grilles",
            "Door frames",
            "Door linings",
            "Door stops",
            "Associated fire stops",
            "Associated smoke stops",
            "Glass, type stated",
            "Louvre blades",
            "Type of item, unit or set stated"
        ]
    },
    "25. Stairs, walkways and balustrades": {
        "keywords": ["staircase", "loft", "ladders", "catwalks", "walkways", "balustrades", "handrails", "barriers", "guard", "rails", "balcony", "units"],
        "items": [
            "Staircase: type stated",
            "Loft ladders",
            "Ladders",
            "Extra over for:",
            "Catwalks",
            "Walkways",
            "Balustrades",
            "Handrails",
            "Barriers",
            "Guard rails",
            "Balcony units",
            "Extra over for:"
        ]
    },
    "26. Metalwork": {
        "keywords": ["isolated", "metal", "members", "general", "metalwork", "sheet", "metal", "wire", "mesh", "composite", "items", "filling", "hollow", "sections", "surface", "treatments", "coatings"],
        "items": [
            "Isolated metal members",
            "General metalwork members",
            "Sheet metal",
            "Wire mesh",
            "Composite items",
            "Filling hollow sections",
            "Surface treatments",
            "Isolated protective coatings"
        ]
    },
    "27. Glazing": {
        "keywords": ["glass", "sealed", "glazed", "units", "louvre", "blades", "lead", "light", "glazing", "saddle", "bars", "mirrors", "removing", "existing"],
        "items": [
            "Glass, type stated",
            "Sealed glazed units, type of glass stated",
            "Louvre blades, type of glass stated",
            "Extra for:",
            "Lead light glazing, type of glass stated",
            "Saddle bars",
            "Mirrors",
            "Removing existing glass and preparing frame or surround to receive new glass"
        ]
    },
    "28. Floor, wall and ceiling and roof finishes": {
        "keywords": ["screeds", "beds", "toppings", "finish", "floors", "raised", "access", "floors", "ramps", "fire", "barriers", "roofs", "walls", "ceilings", "columns", "beams", "treads", "risers", "skirtings", "movement", "joints"],
        "items": [
            "Screeds, beds and toppings, thickness and number of coats stated",
            "Finish to floors, type of finish and overall thickness stated",
            "Raised access floors, type of finish and thickness of panels stated",
            "Ramps to raised access floors",
            "Fire barriers within void below raised floor",
            "Finish to roofs, type of finish and overall thickness stated",
            "Finish to walls, type of finish and overall thickness stated",
            "Finish to isolated columns, type of finish and overall thickness stated",
            "Finish to ceilings, type of finish and overall thickness stated",
            "Finish to isolated beams, type of finish and overall thickness stated",
            "Finish to treads",
            "Finish to risers",
            "Finish to strings and aprons",
            "Skirtings, net height stated",
            "Linings to channels",
            "Kerbs and cappings",
            "Coves",
            "Mouldings",
            "Cornices",
            "Architraves",
            "Ceiling ribs",
            "Bands",
            "Special tiles, slabs or blocks",
            "Surface dressings, sealers or polishes",
            "Movement joints",
            "Cover strips",
            "Dividing strips",
            "Beads, function stated",
            "Nosings",
            "Reinforcement, details stated",
            "Metal mesh lathing, details stated",
            "Board insulation, thickness stated",
            "Quilt insulation, thickness stated",
            "Isolation membranes, thickness stated",
            "Accessories",
            "Precast plaster components"
        ]
    },
    "29. Decoration": {
        "keywords": ["painting", "general", "surfaces", "glazed", "surfaces", "structural", "metalwork", "radiators", "gutters", "pipes", "services", "railings", "fences", "gates", "decorative", "papers", "fabrics", "walls", "columns", "ceilings", "beams", "borders", "motifs"],
        "items": [
            "Painting to general surfaces",
            "Painting to glazed surfaces irrespective of pane sizes",
            "Painting structural metalwork",
            "Painting radiators, type stated",
            "Painting gutters",
            "Painting pipes",
            "Painting services, type stated",
            "Painting railings, fences and gates",
            "Walls and columns",
            "Ceilings and beams",
            "Borders",
            "Motifs"
        ]
    },
    "30. Suspended ceilings": {
        "keywords": ["ceilings", "plenum", "ceilings", "beams", "bulkheads", "isolated", "strips", "upstands", "access", "panels", "edge", "trims", "angle", "trims", "fire", "barriers", "collars", "fittings", "shadow", "gap", "battens"],
        "items": [
            "Ceilings",
            "Plenum ceilings",
            "Beams",
            "Bulkheads",
            "Isolated strips",
            "Upstands",
            "Access panels",
            "Edge trims",
            "Angle trims",
            "Fire barriers",
            "Collars for services passing through fire barriers",
            "Fittings",
            "Shadow gap battens"
        ]
    },
    "31. Insulation, fire stopping and fire protection": {
        "keywords": ["boards", "sheets", "quilts", "loose", "sprayed", "filling", "cavities", "fire", "stops", "fire", "sleeves", "collars"],
        "items": [
            "Boards",
            "Sheets",
            "Quilts",
            "Loose",
            "Sprayed",
            "Filling cavities",
            "Fire stops, type stated",
            "Fire sleeves, collars and the like"
        ]
    },
    "32. Furniture, fittings and equipment": {
        "keywords": ["fixtures", "fittings", "equipment", "services", "ancillary", "items", "employer", "signwriting"],
        "items": [
            "Fixtures, fittings or equipment without services",
            "Fixtures, fittings or equipment with services",
            "Ancillary items not provided with the item of equipment",
            "Fixtures, fittings or equipment supplied by the employer",
            "Signwriting"
        ]
    },
    "33. Drainage above ground": {
        "keywords": ["pipework", "pipework", "ancillaries", "extra", "over", "pipe", "sleeves", "walls", "floors", "ceilings", "gutters", "gutter", "ancillaries", "marking", "identification", "testing", "commissioning", "drawings", "manuals"],
        "items": [
            "Pipework",
            "Pipework ancillaries",
            "Items extra over the pipe in which they occur",
            "Pipe sleeves through walls, floors and ceilings",
            "Gutters",
            "Gutter ancillaries",
            "Items extra over the gutter in which they occur",
            "Marking, position of and leaving or forming all holes, mortices, chases and the like required in the structure",
            "Identification",
            "Testing and commissioning",
            "Preparing drawings",
            "Operating manuals and instructions"
        ]
    },
    "34. Drainage below ground": {
        "keywords": ["drain", "runs", "extra", "over", "drain", "runs", "pipe", "fittings", "accessories", "pumps", "manholes", "inspection", "chambers", "soakaways", "cesspits", "septic", "tanks", "covers", "frames", "connections", "testing"],
        "items": [
            "Drain runs",
            "Items extra over drain runs irrespective of depth or pipe size",
            "Pipe fittings",
            "Accessories",
            "Pumps",
            "Manholes",
            "Inspection chambers",
            "Soakaways",
            "Cesspits",
            "Septic tanks",
            "Other tanks and pits, type stated",
            "Extra over the excavation for:",
            "Sundries",
            "Covers and frames",
            "Marker posts",
            "Connections",
            "Testing and commissioning"
        ]
    },
    "35. Site works": {
        "keywords": ["kerbs", "edgings", "channels", "paving", "accessories", "concrete", "formwork", "reinforcement", "joints", "worked", "finishes", "macadam", "asphalt", "gravel", "hoggin", "woodchip", "interlocking", "brick", "blocks", "slabs", "site", "furniture", "surfacings", "markings"],
        "items": [
            "Kerbs",
            "Edgings",
            "Channels",
            "Paving accessories",
            "Extra over for:",
            "In-situ concrete",
            "Formwork",
            "Reinforcement",
            "Joints",
            "Worked finishes",
            "Accessories cast in",
            "Coated macadam and asphalt",
            "Gravel, hoggin and woodchip",
            "Interlocking brick and blocks, slabs, bricks, blocks, setts and cobbles",
            "Extra over for:",
            "Accessories",
            "Site furniture",
            "Liquid applied surfacings",
            "Sheet surfacings",
            "Tufted surfacings",
            "Proprietary coloured sports surfacings",
            "Surface dressings",
            "Line markings, width stated",
            "Letters, figures and symbols",
            "Sheet linings to pools, lakes, ponds, waterways and the like",
            "Spot items"
        ]
    },
    "36. Fencing": {
        "keywords": ["fencing", "special", "supports", "independent", "gate", "posts", "extra", "over", "fencing", "supports", "gates", "ironmongery"],
        "items": [
            "Fencing, type stated",
            "Extra over for special supports",
            "Independent gate posts",
            "Items extra over fencing, supports and special supports and independent gate posts irrespective of type",
            "Gates",
            "Ironmongery"
        ]
    },
    "37. Soft landscapping": {
        "keywords": ["cultivating", "surface", "applications", "seeding", "turfing", "trees", "young", "nursery", "stock", "trees", "shrubs", "hedge", "plants", "plants", "bulbs", "corms", "tubers", "plant", "containers", "protection", "maintenance"],
        "items": [
            "Cultivating",
            "Surface applications",
            "Seeding",
            "Turfing",
            "Trees",
            "Young nursery stock trees",
            "Shrubs",
            "Hedge plants",
            "Plants",
            "Bulbs, corms and tubers",
            "Plant containers",
            "Protection",
            "Maintenance"
        ]
    },
    "38. Mechanical services": {
        "keywords": ["primary", "equipment", "terminal", "equipment", "fittings", "pipework", "pipe", "fittings", "pipe", "ancillaries", "ventilation", "ducts", "duct", "fittings", "duct", "ancillaries", "insulation", "fire", "protection", "identification", "testing", "commissioning", "validation", "manuals", "training"],
        "items": [
            "Primary equipment",
            "Terminal equipment and fittings",
            "Pipework",
            "Alternative 1 – pipe fittings",
            "Pipe ancillaries",
            "Ventilation ducts",
            "Alternative 1 – duct fittings",
            "Duct ancillaries",
            "Insulation and fire protection",
            "Alternative 1 – Insulation and fire protection to pipe fittings",
            "Insulation and fire protection to pipe ancillaries",
            "Insulation and fire protection to ventilation ducts",
            "Alternative 1 – Insulation and fire protection to duct fittings",
            "Insulation and fire protection to equipment",
            "Fire stopping",
            "Identification",
            "Testing",
            "Commissioning",
            "System validation",
            "Operation and maintenance manuals",
            "Drawing preparation",
            "Training",
            "Loose ancillaries",
            "Post-completion services"
        ]
    },
    "39. Electrical services": {
        "keywords": ["primary", "equipment", "terminal", "equipment", "fittings", "cable", "containment", "cable", "containment", "fittings", "cables", "cable", "terminations", "joints", "final", "circuits", "modular", "wiring", "busbar", "tapes", "electrodes", "earth", "rods", "fire", "stopping", "identification", "testing", "commissioning", "validation", "manuals", "training"],
        "items": [
            "Primary equipment—cont.",
            "Terminal equipment and Fittings",
            "Cable containment",
            "Alternative 1 – cable containment fittings",
            "Cables",
            "Cable terminations and joints",
            "Final circuits",
            "Modular wiring systems",
            "Busbar",
            "Alternative 1 – busbar fittings",
            "Tapes",
            "Electrodes, earth rods, air terminations, termination bars",
            "Fire stopping and other associated fire protect work",
            "Identification",
            "Testing",
            "Commissioning",
            "System validation",
            "Operation and maintenance manuals",
            "Drawing preparation",
            "Training",
            "Loose ancillaries",
            "Post practical completion Services"
        ]
    },
    "40. Transportation": {
        "keywords": ["system", "fire", "stopping", "identification", "testing", "commissioning", "validation", "manuals", "drawing", "training", "ancillaries", "completion"],
        "items": [
            "System",
            "Fire stopping and other associated fire protect work",
            "Identification",
            "Testing and commissioning",
            "System validation",
            "Operation and maintenance manuals",
            "Drawing preparation",
            "Training",
            "Loose ancillaries",
            "Post practical completion services"
        ]
    },
    "41. Builders work in connection with mechanical, electrical and transportation installations": {
        "keywords": ["general", "builder's", "work", "marking", "position", "holes", "mortices", "chases", "structure", "pipe", "duct", "sleeves", "bases", "plinths", "duct", "covers", "frames", "supports", "services", "catenary", "cables", "cutting", "existing", "structures", "underground", "service", "runs", "manholes", "chambers", "connections"],
        "items": [
            "General builder's work in connection with:",
            "Marking position of holes, mortices and chases in the structure",
            "Pipe and duct sleeves",
            "Bases, plinths and the like",
            "Duct covers and frames",
            "Supports for services not provided by services contractor",
            "Catenary cables",
            "Cutting holes through existing structures",
            "Cutting mortices and sinkings in existing structure",
            "Cutting chases through existing structures",
            "Lifting and replacing floor boards",
            "Lifting and replacing duct covers or chequer plates",
            "Underground service runs",
            "Items extra over service runs irrespective of depth or pipe size",
            "Pipe duct fittings",
            "Accessories",
            "Manholes",
            "Access chambers",
            "Valve chambers",
            "Inspection chambers",
            "Surface boxes",
            "Stopcock pits",
            "Extra over the excavation for:",
            "Marker posts",
            "Marker plates",
            "Connections",
            "Testing and commissioning"
        ]
    }
}

SECTION_ORDER = list(BOQ_TEMPLATE.keys())

# -----------------------
# BOQ Template will be loaded externally
# -----------------------
# Initialize empty template - to be loaded from external source



def load_boq_template():
    """Load BOQ template from external source"""
    global BOQ_TEMPLATE, SECTION_ORDER
    # This will be populated from your external BOQ template
    # For now, we'll use a minimal fallback
    if not BOQ_TEMPLATE:
        BOQ_TEMPLATE = {
            "1. Preliminaries": {
                "keywords": ["management", "staff", "accommodation", "temporary"],
                "items": ["Project management", "Site establishment", "Temporary works"]
            },
            "11. Insitu concrete works": {
                "keywords": ["concrete", "foundation", "slab", "beam", "column"],
                "items": ["Mass concrete", "Reinforced concrete", "Formwork"]
            },
            "14. Masonry": {
                "keywords": ["brick", "block", "wall", "masonry"],
                "items": ["Brick walls", "Block walls", "Cavity walls"]
            }
        }
        SECTION_ORDER = list(BOQ_TEMPLATE.keys())


# -----------------------
# Enhanced extraction functions
# -----------------------
class BOQExtractor:
    def __init__(self):
        self.section_scores = {}
        load_boq_template()

    def calculate_relevance_score(self, text: str, section: str, keywords: List[str]) -> float:
        """Calculate relevance score for a section based on keyword matching"""
        text_lower = text.lower()
        score = 0
        total_keywords = len(keywords)

        for keyword in keywords:
            if keyword in text_lower:
                # Weight longer keywords more heavily
                weight = len(keyword) / 5
                score += weight

        return score / total_keywords if total_keywords > 0 else 0

    def extract_quantities_and_units(self, text: str) -> List[Tuple[float, str]]:
        """Extract quantities and units from text"""
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(m2|sqm|square\s*meter)',
            r'(\d+(?:\.\d+)?)\s*(m3|cum|cubic\s*meter)',
            r'(\d+(?:\.\d+)?)\s*(m|meter|linear\s*meter)',
            r'(\d+(?:\.\d+)?)\s*(nr|no|number|each)',
            r'(\d+(?:\.\d+)?)\s*(kg|kilogram)',
            r'(\d+(?:\.\d+)?)\s*(tonnes?|tons?)',
        ]

        quantities = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                qty = float(match[0])
                unit = match[1].lower()
                # Normalize units
                if unit in ['sqm', 'square meter']:
                    unit = 'm2'
                elif unit in ['cum', 'cubic meter']:
                    unit = 'm3'
                elif unit in ['meter', 'linear meter']:
                    unit = 'm'
                elif unit in ['no', 'number', 'each']:
                    unit = 'nr'
                quantities.append((qty, unit))

        return quantities

    def intelligent_extract(self, project_description: str) -> Dict:
        """Enhanced rule-based extraction with intelligent scoring"""
        text = project_description.lower()
        structured = {}

        # Calculate relevance scores for all sections
        for section, data in BOQ_TEMPLATE.items():
            keywords = data["keywords"]
            score = self.calculate_relevance_score(text, section, keywords)
            self.section_scores[section] = score

        # Sort sections by relevance
        sorted_sections = sorted(self.section_scores.items(), key=lambda x: x[1], reverse=True)

        # Extract quantities once
        quantities = self.extract_quantities_and_units(project_description)

        # Only include sections with score > threshold
        threshold = 0.1
        for section, score in sorted_sections:
            if score > threshold:
                items_data = BOQ_TEMPLATE[section]["items"]
                keywords = BOQ_TEMPLATE[section]["keywords"]

                relevant_items = []
                for item in items_data:
                    item_keywords = item.lower().split()
                    item_relevance = any(kw in text for kw in item_keywords if len(kw) > 3)

                    if item_relevance or score > 0.5:
                        # Try to match quantities
                        qty = 1
                        unit = "LS"

                        # Use extracted quantities if available
                        if quantities:
                            qty, unit = quantities[0]
                        else:
                            # Smart unit assignment based on item type
                            if any(word in item.lower() for word in ["wall", "floor", "ceiling", "roof"]):
                                unit = "m2"
                                qty = 0
                            elif any(word in item.lower() for word in ["excavation", "concrete", "fill"]):
                                unit = "m3"
                                qty = 0
                            elif any(word in item.lower() for word in ["pipe", "cable", "length"]):
                                unit = "m"
                                qty = 0

                        relevant_items.append({
                            "item": item,
                            "qty": qty,
                            "unit": unit,
                            "rate": 0.0,
                            "amount": 0.0,
                            "notes": f"Auto-detected (relevance: {score:.2f})"
                        })

                if relevant_items:
                    structured[section] = relevant_items

        # Always include Preliminaries if nothing detected
        if not structured:
            structured["1. Preliminaries"] = [{
                "item": "Project specific management and staff",
                "qty": 1,
                "unit": "LS",
                "rate": 0.0,
                "amount": 0.0,
                "notes": "Default inclusion"
            }]

        return structured


# -----------------------
# Gemini wrapper (enhanced with hardcoded API key)
# -----------------------
def configure_gemini():
    """Configure Gemini with hardcoded API key"""
    if not GEMINI_AVAILABLE:
        raise RuntimeError("google.generativeai not installed.")
    genai.configure(api_key=GEMINI_API_KEY)


def call_gemini_extract(project_description: str) -> str:
    """Call Gemini API for BOQ extraction"""
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
You are an expert quantity surveyor. Analyze this project description and create a comprehensive Bill of Quantities.

Project description:
\"\"\"{project_description}\"\"\"

Instructions:
1. Identify relevant construction work sections (e.g., Preliminaries, Excavation, Concrete, Masonry, etc.)
2. For each section, list specific work items that would be required
3. Extract or estimate quantities from the description where possible
4. Return each item in this EXACT format:
SECTION | ITEM | QTY | UNIT | RATE | AMOUNT | NOTES

Guidelines:
- Use standard units: m2 for areas, m3 for volumes, m for lengths, nr for counted items, LS for lump sum
- If quantity is unknown, use 0 and note "Quantity to be confirmed"
- If rate is unknown, use 0 and note "Rate to be confirmed"
- Focus on items that are clearly relevant to this specific project
- Include preliminaries, main construction items, finishes, and services as applicable

Example format:
1. Preliminaries | Project management | 1 | LS | 0 | 0 | Rate to be confirmed
5. Excavation and filling | Site excavation | 150 | m3 | 0 | 0 | Quantity estimated from description
"""

    response = model.generate_content(prompt)
    return response.text


# -----------------------
# Parsing and data processing functions
# -----------------------
def parse_gemini_lines_to_structured(text_lines: str) -> Dict:
    """Parse Gemini output with better error handling"""
    structured = {}
    for raw_line in text_lines.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or len(line.split('|')) < 6:
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 6:
            section, item, qty, unit, rate, amount = parts[:6]
            notes = parts[6] if len(parts) > 6 else ""

            try:
                qty_val = float(qty) if qty and qty != '0' else 0.0
                rate_val = float(rate) if rate and rate != '0' else 0.0
                amount_val = float(amount) if amount else qty_val * rate_val
            except (ValueError, TypeError):
                qty_val = 0.0
                rate_val = 0.0
                amount_val = 0.0

            row = {
                "item": item,
                "qty": qty_val,
                "unit": unit or "LS",
                "rate": rate_val,
                "amount": amount_val,
                "notes": notes or "Extracted by AI"
            }

            structured.setdefault(section, []).append(row)

    return structured


def structured_to_item_df(structured_boq: Dict) -> pd.DataFrame:
    """Convert structured BOQ to DataFrame"""
    rows = []
    for section, items in structured_boq.items():
        for item_data in items:
            rows.append({
                "Section": section,
                "Item Description": item_data["item"],
                "Qty": item_data["qty"],
                "Unit": item_data["unit"],
                "Rate": item_data["rate"],
                "Amount": item_data["amount"],
                "Notes": item_data["notes"]
            })

    df = pd.DataFrame(rows)
    # Ensure numeric columns are properly typed
    for col in ["Qty", "Rate", "Amount"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df


def build_summary_dataframe(structured_boq: Dict) -> pd.DataFrame:
    """Build summary with proper ordering and totals"""
    rows = []
    total = 0.0

    # Process all sections
    for section, items in structured_boq.items():
        section_amount = sum(item.get("amount", 0) for item in items)
        rows.append({"Bill Description": section, "Amount": section_amount})
        total += section_amount

    # Add total row
    rows.append({"Bill Description": "TOTAL", "Amount": total})

    return pd.DataFrame(rows)


# PDF and Excel export functions
def df_to_excel_bytes(summary_df: pd.DataFrame, items_df: pd.DataFrame, project_meta: Dict) -> bytes:
    with io.BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            # Main detailed BOQ sheet
            items_df.to_excel(writer, sheet_name="BOQ_DETAILED", index=False)
            # Summary as secondary sheet
            summary_df.to_excel(writer, sheet_name="SUMMARY", index=False)
            # Project metadata
            pd.DataFrame([project_meta]).to_excel(writer, sheet_name="PROJECT_INFO", index=False)
        return buffer.getvalue()


def df_to_pdf_bytes(summary_df: pd.DataFrame, items_df: pd.DataFrame, project_meta: Dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    # Header
    elements.append(Paragraph(f"BILL OF QUANTITIES - DETAILED", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Project: {project_meta.get('Project', 'N/A')}", styles['Heading2']))
    elements.append(Paragraph(f"Location: {project_meta.get('Location', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"Client: {project_meta.get('Client', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {project_meta.get('Generated', 'N/A')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Detailed Items table (main content)
    elements.append(Paragraph("DETAILED BILL OF QUANTITIES", styles['Heading2']))

    # Format numeric columns for better display
    items_display = items_df.copy()
    items_display['Qty'] = items_display['Qty'].round(2)
    items_display['Rate'] = items_display['Rate'].round(2)
    items_display['Amount'] = items_display['Amount'].round(2)

    items_data = [items_display.columns.tolist()] + items_display.values.tolist()
    items_table = Table(items_data, hAlign='LEFT')
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (5, -1), 'RIGHT'),  # Right align numeric columns
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 30))

    # Summary table (secondary)
    elements.append(Paragraph("SUMMARY", styles['Heading3']))
    summary_data = [summary_df.columns.tolist()] + summary_df.round(2).values.tolist()
    summary_table = Table(summary_data, hAlign='LEFT')
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Right align amounts
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.yellow),  # Highlight total row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


# -----------------------
# Streamlit UI (Simplified without API key input)
# -----------------------
def main():
    st.set_page_config(
        page_title="AI-Assisted BOQ Generator",
        page_icon="🏗️",
        layout="wide"
    )

    st.title("🏗️ AI-Assisted BOQ Generator")
    st.markdown("Generate comprehensive Bills of Quantities from project descriptions using AI assistance")

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Project metadata
        st.subheader("Project Details")
        project_name = st.text_input("Project Name", placeholder="Enter project name")
        project_location = st.text_input("Location", placeholder="Project location")
        project_client = st.text_input("Client", placeholder="Client name")

        st.divider()

        # AI Configuration (simplified)
        st.subheader("AI Settings")
        use_gemini = st.checkbox("Use Gemini AI", value=True, help="Enable AI-powered extraction")

        if use_gemini and not GEMINI_AVAILABLE:
            st.error("❌ Gemini AI not available. Please install google-generativeai package.")
            use_gemini = False

        st.divider()

        # Quick examples
        st.subheader("📋 Example Projects")
        if st.button("Load Residential Example"):
            st.session_state.example_text = """
            Two-story residential house construction:
            - 150 sqm ground floor area
            - 120 sqm first floor area  
            - Brick masonry walls with cavity insulation
            - Reinforced concrete foundations and ground floor slab
            - Timber frame roof with tile covering
            - Internal plastering and painting
            - Electrical installation with lighting and power points
            - Plumbing with kitchen and 2 bathrooms
            - HVAC system installation
            - Landscaping and driveway
            """

        if st.button("Load Commercial Example"):
            st.session_state.example_text = """
            Office building construction:
            - 500 sqm per floor, 3 floors
            - Steel frame structure
            - Precast concrete floor slabs
            - Curtain wall glazing system
            - Suspended ceiling throughout
            - Mechanical ventilation system
            - Fire protection systems
            - Electrical services including data cabling
            - Lift installation
            - Car park with 20 spaces
            """

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Project Description")
        project_description = st.text_area(
            "Describe your construction project in detail:",
            height=300,
            value=st.session_state.get('example_text', ''),
            placeholder="Enter detailed project description including materials, quantities, and scope of work..."
        )

        # Analysis button
        analyze_button = st.button("🔍 Generate BOQ", type="primary", use_container_width=True)

    with col2:
        st.subheader("📊 Extraction Stats")
        if 'section_scores' in st.session_state:
            scores_df = pd.DataFrame(
                [(k.split('.')[1].strip() if '.' in k else k, v) for k, v in st.session_state.section_scores.items()],
                columns=['Section', 'Relevance Score']
            ).sort_values('Relevance Score', ascending=False)
            st.dataframe(scores_df, use_container_width=True)

    # Processing
    if analyze_button and project_description.strip():
        with st.spinner("🤖 Analyzing project and generating BOQ..."):
            extractor = BOQExtractor()
            structured = {}

            try:
                if use_gemini:
                    configure_gemini()
                    gemini_response = call_gemini_extract(project_description)
                    structured = parse_gemini_lines_to_structured(gemini_response)

                    if not structured:
                        st.info("🔄 AI returned limited results, using intelligent fallback...")
                        structured = extractor.intelligent_extract(project_description)
                    else:
                        st.success("✅ AI extraction completed successfully!")
                else:
                    structured = extractor.intelligent_extract(project_description)
                    st.info("📋 Using intelligent rule-based extraction")

                # Store section scores for display
                st.session_state.section_scores = extractor.section_scores

            except Exception as e:
                st.error(f"❌ Error during extraction: {str(e)}")
                st.info("🔄 Falling back to rule-based extraction...")
                structured = extractor.intelligent_extract(project_description)

        if structured:
            # Convert to DataFrames and store in session state
            items_df = structured_to_item_df(structured)
            st.session_state.items_df = items_df
            st.session_state.boq_generated = True

    # Display BOQ data if available in session state
    if st.session_state.get('boq_generated', False) and 'items_df' in st.session_state:
        st.subheader("✏️ Review and Edit Items")
        st.info("💡 Edit quantities and rates. Amounts will be auto-calculated.")

        # Initialize edited_df_key if not exists
        if 'edited_df_key' not in st.session_state:
            st.session_state.edited_df_key = 0

        # Create a copy to avoid reference issues
        current_df = st.session_state.items_df.copy()

        # Recalculate amounts before displaying
        try:
            current_df["Amount"] = pd.to_numeric(current_df["Qty"], errors='coerce').fillna(0) * \
                                   pd.to_numeric(current_df["Rate"], errors='coerce').fillna(0)
        except Exception:
            st.warning("⚠️ Error calculating amounts. Please check numeric values.")

        # Editable data table using session state with unique key
        edited_df = st.data_editor(
            current_df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"boq_editor_{st.session_state.edited_df_key}",
            column_config={
                "Qty": st.column_config.NumberColumn("Quantity", format="%.2f"),
                "Rate": st.column_config.NumberColumn("Rate (£)", format="£%.2f"),
                "Amount": st.column_config.NumberColumn("Amount (£)", format="£%.2f", disabled=True)
            },
            hide_index=True
        )

        # Check if data has been edited and update session state
        if not edited_df.equals(current_df):
            # Recalculate amounts for edited data
            edited_df["Amount"] = pd.to_numeric(edited_df["Qty"], errors='coerce').fillna(0) * \
                                  pd.to_numeric(edited_df["Rate"], errors='coerce').fillna(0)

            # Update session state
            st.session_state.items_df = edited_df.copy()

        # Use the current dataframe for calculations
        working_df = edited_df

        # Generate summary
        summary_df = working_df.groupby("Section", sort=False)["Amount"].sum().reset_index()
        summary_df.columns = ["Bill Description", "Amount"]

        # Add total row
        total_amount = summary_df["Amount"].sum()
        summary_df = pd.concat([
            summary_df,
            pd.DataFrame([{"Bill Description": "TOTAL", "Amount": total_amount}])
        ], ignore_index=True)

        # Display summary
        st.subheader("📋 Bill of Quantities Summary")
        st.dataframe(
            summary_df.style.format({"Amount": "£{:.2f}"}),
            use_container_width=True
        )

        # Clear BOQ button
        if st.button("🗑️ Clear BOQ and Start Over", type="secondary"):
            for key in ['boq_generated', 'items_df', 'section_scores', 'edited_df_key']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        # Project metadata for export
        project_meta = {
            "Project": project_name or "Unnamed Project",
            "Location": project_location or "Not specified",
            "Client": project_client or "Not specified",
            "Generated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
        }

        # Export buttons
        st.subheader("📥 Export Options")
        col1, col2 = st.columns(2)

        with col1:
            excel_bytes = df_to_excel_bytes(summary_df, working_df, project_meta)
            st.download_button(
                "📊 Download Excel",
                data=excel_bytes,
                file_name=f"BOQ_{project_name or 'project'}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col2:
            pdf_bytes = df_to_pdf_bytes(summary_df, working_df, project_meta)
            st.download_button(
                "📄 Download PDF",
                data=pdf_bytes,
                file_name=f"BOQ_{project_name or 'project'}_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        st.success("🎉 BOQ generated successfully!")

    elif analyze_button:
        st.warning("⚠️ Please enter a project description before generating the BOQ.")


if __name__ == "__main__":
    main()