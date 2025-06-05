# symbolic_constants.py

# Core sigil glyphs for symbolic token representation (100)
# proto_sigils_1000_grouped.py

PROTO_SIGILS = [
    "∀", "∁", "∂", "∃", "∄", "∅", "∆", "∇", "∈", "∉", "∊", "∋", "∌", "∍", "∎", "∏", "∐", "∑", "−", "∓",
    "∔", "∕", "∖", "∗", "∘", "∙", "√", "∛", "∜", "∝", "∞", "∟", "∠", "∡", "∢", "∤", "∥", "∦", "∧", "∨",
    "∩", "∪", "∫", "∬", "∭", "∮", "∯", "∰", "∱", "∲", "∳", "∴", "∵", "∶", "∷", "∸", "∹", "∺", "∻", "∼",
    "∽", "∾", "∿", "≀", "≁", "≂", "≃", "≄", "≅", "≆", "≇", "≈", "≉", "≊", "≋", "≌", "≍", "≎", "≏", "≐",
    "≑", "≒", "≓", "≔", "≕", "≖", "≗", "≘", "≙", "≚", "≛", "≜", "≝", "≞", "≟", "≠", "≡", "≢", "≣", "≤",
    "≥", "≦", "≧", "≨", "≩", "≪", "≫", "≬", "≭", "≮", "≯", "≰", "≱", "≲", "≳", "≴", "≵", "≶", "≷", "≸",
    "≹", "≺", "≻", "≼", "≽", "≾", "≿", "⊀", "⊁", "⊂", "⊃", "⊄", "⊅", "⊆", "⊇", "⊈", "⊉", "⊊", "⊋", "⊌",
    "⊍", "⊎", "⊏", "⊐", "⊑", "⊒", "⊓", "⊔", "⊕", "⊖", "⊗", "⊘", "⊙", "⊚", "⊛", "⊜", "⊝", "⊞", "⊟", "⊠",
    "⊡", "⊢", "⊣", "⊤", "⊥", "⊦", "⊧", "⊨", "⊩", "⊪", "⊫", "⊬", "⊭", "⊮", "⊯", "⊰", "⊱", "⊲", "⊳", "⊴",
    "⊵", "⊶", "⊷", "⊸", "⊹", "⊺", "⊻", "⊼", "⊽", "⊾", "⊿", "⋀", "⋁", "⋂", "⋃", "⋄", "⋅", "⋆", "⋇", "⋈",
    "⋉", "⋊", "⋋", "⋌", "⋍", "⋎", "⋏", "⋐", "⋑", "⋒", "⋓", "⋔", "⋕", "⋖", "⋗", "⋘", "⋙", "⋚", "⋛", "⋜",
    "⋝", "⋞", "⋟", "⋠", "⋡", "⋢", "⋣", "⋤", "⋥", "⋦", "⋧", "⋨", "⋩", "⋪", "⋫", "⋬", "⋭", "⋮", "⋯", "⋰",
    "⋱", "⋲", "⋳", "⋴", "⋵", "⋶", "⋷", "⋸", "⋹", "⋺", "⋻", "⋼", "⋽", "⋾", "⋿", "⌀", "⌁", "⌂", "⌃", "⌄",
    "⌅", "⌆", "⌇", "⌈", "⌉", "⌊", "⌋", "⌌", "⌍", "⌎", "⌏", "⌐", "⌑", "⌒", "⌓", "⌔", "⌕", "⌖", "⌗", "⌘",
    "⌙", "⌚", "⌛", "⌜", "⌝", "⌞", "⌟", "⌠", "⌡", "⌢", "⌣", "⌤", "⌥", "⌦", "⌧", "⌨", "〈", "〉", "⌫", "⌬",
    "⌭", "⌮", "⌯", "⌰", "⌱", "⌲", "⌳", "⌴", "⌵", "⌶", "⌷", "⌸", "⌹", "⌺", "⌻", "⌼", "⌽", "⌾", "⌿", "⍀",
    "⍁", "⍂", "⍃", "⍄", "⍅", "⍆", "⍇", "⍈", "⍉", "⍊", "⍋", "⍌", "⍍", "⍎", "⍏", "⍐", "⍑", "⍒", "⍓", "⍔",
    "⍕", "⍖", "⍗", "⍘", "⍙", "⍚", "⍛", "⍜", "⍝", "⍞", "⍟", "⍠", "⍡", "⍢", "⍣", "⍤", "⍥", "⍦", "⍧", "⍨",
    "⍩", "⍪", "⍫", "⍬", "⍭", "⍮", "⍯", "⍰", "⍱", "⍲", "⍳", "⍴", "⍵", "⍶", "⍷", "⍸", "⍹", "⍺", "⍻", "⍼",
    "⍽", "⍾", "⍿", "⎀", "⎁", "⎂", "⎃", "⎄", "⎅", "⎆", "⎇", "⎈", "⎉", "⎊", "⎋", "⎌", "⎍", "⎎", "⎏", "⎐",
    "⎑", "⎒", "⎓", "⎔", "⎕", "⎖", "⎗", "⎘", "⎙", "⎚", "⎛", "⎝", "⎞", "⎠", "⎡", "⎣", "⎤", "⎦", "⎧", "⎨",
    "⎩", "⎪", "⎫", "⎬", "⎭", "⎯", "⎰", "⎱", "⎲", "⎳", "⎴", "⎵", "⎶", "⎷", "⎸", "⎹", "⎺", "⎻", "⎼", "⎽",
    "⎾", "⎿", "⏀", "⏁", "⏂", "⏃", "⏄", "⏅", "⏆", "⏇", "⏈", "⏉", "⏊", "⏋", "⏌", "⏍", "⏎", "⏏", "⏐", "⏑",
    "⏒", "⏓", "⏔", "⏕", "⏖", "⏗", "⏘", "⏙", "⏚", "⏛", "⏜", "⏝", "⏞", "⏟", "⏠", "⏡", "⏢", "⏣", "⏤", "⏥",
    "⏦", "⏧", "⏨", "⏩", "⏪", "⏫", "⏬", "⏭", "⏮", "⏯", "⏰", "⏱", "⏲", "⏳", "⏴", "⏵", "⏶", "⏷", "⏸", "⏹",
    "⏺", "⏻", "⏼", "⏽", "⏾", "⏿", "␀", "␁", "␂", "␃", "␄", "␅", "␆", "␇", "␈", "␉", "␊", "␋", "␌", "␍",
    "␎", "␏", "␐", "␑", "␒", "␓", "␔", "␕", "␖", "␗", "␘", "␙", "␚", "␛", "␜", "␝", "␞", "␟", "␠", "␡",
    "␢", "␣", "␤", "␥", "␦", "␧", "␨", "␩", "␪", "␫", "␬", "␭", "␮", "␯", "␰", "␱", "␲", "␳", "␴", "␵",
    "␶", "␷", "␸", "␹", "␺", "␻", "␼", "␽", "␾", "␿", "⑀", "⑁", "⑂", "⑃", "⑄", "⑅", "⑆", "⑇", "⑈", "⑉",
    "⑊", "⑋", "⑌", "⑍", "⑎", "⑏", "⑐", "⑑", "⑒", "⑓", "⑔", "⑕", "⑖", "⑗", "⑘", "⑙", "⑚", "⑛", "⑜", "⑝",
    "⑞", "⑟", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩", "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱",
    "⑲", "⑳", "⑴", "⑵", "⑶", "⑷", "⑸", "⑹", "⑺", "⑻", "⑼", "⑽", "⑾", "⑿", "⒀", "⒁", "⒂", "⒃", "⒄", "⒅",
    "⒆", "⒇", "⒈", "⒉", "⒊", "⒋", "⒌", "⒍", "⒎", "⒏", "⒐", "⒑", "⒒", "⒓", "⒔", "⒕", "⒖", "⒗", "⒘", "⒙",
    "⒚", "⒛", "⒜", "⒝", "⒞", "⒟", "⒠", "⒡", "⒢", "⒣", "⒤", "⒥", "⒦", "⒧", "⒨", "⒩", "⒪", "⒫", "⒬", "⒭",
    "⒮", "⒯", "⒰", "⒱", "⒲", "⒳", "⒴", "⒵", "Ⓐ", "Ⓑ", "Ⓒ", "Ⓓ", "Ⓔ", "Ⓕ", "Ⓖ", "Ⓗ", "Ⓘ", "Ⓙ", "Ⓚ", "Ⓛ",
    "Ⓜ", "Ⓝ", "Ⓞ", "Ⓟ", "Ⓠ", "Ⓡ", "Ⓢ", "Ⓣ", "Ⓤ", "Ⓥ", "Ⓦ", "Ⓧ", "Ⓨ", "Ⓩ", "ⓐ", "ⓑ", "ⓒ", "ⓓ", "ⓔ", "ⓕ",
    "ⓖ", "ⓗ", "ⓘ", "ⓙ", "ⓚ", "ⓛ", "ⓜ", "ⓝ", "ⓞ", "ⓟ", "ⓠ", "ⓡ", "ⓢ", "ⓣ", "ⓤ", "ⓥ", "ⓦ", "ⓧ", "ⓨ", "ⓩ",
    "⓪", "⓫", "⓬", "⓭", "⓮", "⓯", "⓰", "⓱", "⓲", "⓳", "⓴", "⓵", "⓶", "⓷", "⓸", "⓹", "⓺", "⓻", "⓼", "⓽",
    "⓾", "⓿", "─", "━", "┃", "┄", "┅", "┇", "┈", "┉", "┋", "┌", "┍", "┎", "┏", "┐", "┑", "┒", "┓", "└",
    "┕", "┖", "┗", "┘", "┙", "┚", "┛", "├", "┝", "┞", "┟", "┠", "┡", "┢", "┣", "┤", "┥", "┦", "┧", "┨",
    "┩", "┪", "┫", "┬", "┭", "┮", "┯", "┰", "┱", "┲", "┳", "┴", "┵", "┶", "┷", "┸", "┹", "┺", "┻", "┼",
    "┽", "┾", "┿", "╀", "╁", "╂", "╃", "╄", "╅", "╆", "╇", "╈", "╉", "╊", "╋", "╌", "╍", "╏", "═", "║",
    "╒", "╓", "╔", "╕", "╖", "╗", "╘", "╙", "╚", "╛", "╜", "╝", "╞", "╟", "╠", "╡", "╢", "╣", "╤", "╥",
    "╦", "╧", "╨", "╩", "╪", "╫", "╬", "╭", "╮", "╯", "╰", "╱", "╲", "╳", "╴", "╶", "╸", "╹", "╺", "╻",
    "╼", "╽", "╾", "╿", "▀", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▉", "▊", "▋", "▌", "▍", "▎", "▏",
    "▐", "░", "▒", "▓", "▔", "▕", "▖", "▗", "▘", "▙", "▚", "▛", "▜", "▝", "▞", "▟", "■", "□", "▢", "▣",
    "▤", "▥", "▦", "▧", "▨", "▩", "▪", "▫", "▬", "▭", "▮", "▯", "▰", "▱", "▲", "△", "▴", "▵", "▶", "▷",
    "▸", "▹", "►", "▻", "▼", "▽", "▾", "▿", "◀", "◁", "◂", "◃", "◄", "◅", "◆", "◇", "◈", "◉", "◊", "○",
    "◌", "◍", "◎", "●", "◐", "◑", "◒", "◓", "◔", "◕", "◖", "◗", "◘", "◙", "◚", "◛", "◜", "◝", "◞", "◟",
    "◠", "◡", "◢", "◣", "◤", "◥", "◦", "◧", "◨", "◩", "◪", "◫", "◬", "◭", "◮", "◯", "◰", "◱", "◲", "◳",
]



# Relationship types corresponding to PROTO_SIGILS

PROTO_SIGIL_TOKENS = [
    "glyphline", "glyphnest", "glyphphase", "glyphcrest", "glyphbloom", "glyphspark", "glyphtrace", "glyphlock", "glyphweft", "glyphnode",
    "glyphwake", "glyphcoil", "glyphroot", "glyphveil", "glyphlight", "glyphshift", "glyphgate", "glyphhorn", "glyphdrift", "glyphvault",
    "glyphlink", "glyphburn", "glyphfield", "glyphpulse", "glyphecho", "glyphdust", "glyphring", "glyphburst", "glyphform", "glyphmass",
    "sigline", "signest", "sigphase", "sigcrest", "sigbloom", "sigspark", "sigtrace", "siglock", "sigweft", "signode",
    "sigwake", "sigcoil", "sigroot", "sigveil", "siglight", "sigshift", "siggate", "sighorn", "sigdrift", "sigvault",
    "siglink", "sigburn", "sigfield", "sigpulse", "sigecho", "sigdust", "sigring", "sigburst", "sigform", "sigmass",
    "flareline", "flarenest", "flarephase", "flarecrest", "flarebloom", "flarespark", "flaretrace", "flarelock", "flareweft", "flarenode",
    "flarewake", "flarecoil", "flareroot", "flareveil", "flarelight", "flareshift", "flaregate", "flarehorn", "flaredrift", "flarevault",
    "flarelink", "flareburn", "flarefield", "flarepulse", "flareecho", "flaredust", "flarering", "flareburst", "flareform", "flaremass",
    "toneline", "tonenest", "tonephase", "tonecrest", "tonebloom", "tonespark", "tonetrace", "tonelock", "toneweft", "tonenode",
    "tonewake", "tonecoil", "toneroot", "toneveil", "tonelight", "toneshift", "tonegate", "tonehorn", "tonedrift", "tonevault",
    "tonelink", "toneburn", "tonefield", "tonepulse", "toneecho", "tonedust", "tonering", "toneburst", "toneform", "tonemass",
    "voidline", "voidnest", "voidphase", "voidcrest", "voidbloom", "voidspark", "voidtrace", "voidlock", "voidweft", "voidnode",
    "voidwake", "voidcoil", "voidroot", "voidveil", "voidlight", "voidshift", "voidgate", "voidhorn", "voiddrift", "voidvault",
    "voidlink", "voidburn", "voidfield", "voidpulse", "voidecho", "voiddust", "voidring", "voidburst", "voidform", "voidmass",
    "echoline", "echonest", "echophase", "echocrest", "echobloom", "echospark", "echotrace", "echolock", "echoweft", "echonode",
    "echowake", "echocoil", "echoroot", "echoveil", "echolight", "echoshift", "echogate", "echohorn", "echodrift", "echovault",
    "echolink", "echoburn", "echofield", "echopulse", "echoecho", "echodust", "echoring", "echoburst", "echoform", "echomass",
    "sparkline", "sparknest", "sparkphase", "sparkcrest", "sparkbloom", "sparkspark", "sparktrace", "sparklock", "sparkweft", "sparknode",
    "sparkwake", "sparkcoil", "sparkroot", "sparkveil", "sparklight", "sparkshift", "sparkgate", "sparkhorn", "sparkdrift", "sparkvault",
    "sparklink", "sparkburn", "sparkfield", "sparkpulse", "sparkecho", "sparkdust", "sparkring", "sparkburst", "sparkform", "sparkmass",
    "riftline", "riftnest", "riftphase", "riftcrest", "riftbloom", "riftspark", "rifttrace", "riftlock", "riftweft", "riftnode",
    "riftwake", "riftcoil", "riftroot", "riftveil", "riftlight", "riftshift", "riftgate", "rifthorn", "riftdrift", "riftvault",
    "riftlink", "riftburn", "riftfield", "riftpulse", "riftecho", "riftdust", "riftring", "riftburst", "riftform", "riftmass",
    "pulseline", "pulsenest", "pulsephase", "pulsecrest", "pulsebloom", "pulsespark", "pulsetrace", "pulselock", "pulseweft", "pulsenode",
    "pulsewake", "pulsecoil", "pulseroot", "pulseveil", "pulselight", "pulseshift", "pulsegate", "pulsehorn", "pulsedrift", "pulsevault",
    "pulselink", "pulseburn", "pulsefield", "pulsepulse", "pulseecho", "pulsedust", "pulsering", "pulseburst", "pulseform", "pulsemass",
    "coreline", "corenest", "corephase", "corecrest", "corebloom", "corespark", "coretrace", "corelock", "coreweft", "corenode",
    "corewake", "corecoil", "coreroot", "coreveil", "corelight", "coreshift", "coregate", "corehorn", "coredrift", "corevault",
    "corelink", "coreburn", "corefield", "corepulse", "coreecho", "coredust", "corering", "coreburst", "coreform", "coremass",
    "dreamline", "dreamnest", "dreamphase", "dreamcrest", "dreambloom", "dreamspark", "dreamtrace", "dreamlock", "dreamweft", "dreamnode",
    "dreamwake", "dreamcoil", "dreamroot", "dreamveil", "dreamlight", "dreamshift", "dreamgate", "dreamhorn", "dreamdrift", "dreamvault",
    "dreamlink", "dreamburn", "dreamfield", "dreampulse", "dreamecho", "dreamdust", "dreamring", "dreamburst", "dreamform", "dreammass",
    "waveline", "wavenest", "wavephase", "wavecrest", "wavebloom", "wavespark", "wavetrace", "wavelock", "waveweft", "wavenode",
    "wavewake", "wavecoil", "waveroot", "waveveil", "wavelight", "waveshift", "wavegate", "wavehorn", "wavedrift", "wavevault",
    "wavelink", "waveburn", "wavefield", "wavepulse", "waveecho", "wavedust", "wavering", "waveburst", "waveform", "wavemass",
    "lumeline", "lumenest", "lumephase", "lumecrest", "lumebloom", "lumespark", "lumetrace", "lumelock", "lumeweft", "lumenode",
    "lumewake", "lumecoil", "lumeroot", "lumeveil", "lumelight", "lumeshift", "lumegate", "lumehorn", "lumedrift", "lumevault",
    "lumelink", "lumeburn", "lumefield", "lumepulse", "lumeecho", "lumedust", "lumering", "lumeburst", "lumeform", "lumemass",
    "rootline", "rootnest", "rootphase", "rootcrest", "rootbloom", "rootspark", "roottrace", "rootlock", "rootweft", "rootnode",
    "rootwake", "rootcoil", "rootroot", "rootveil", "rootlight", "rootshift", "rootgate", "roothorn", "rootdrift", "rootvault",
    "rootlink", "rootburn", "rootfield", "rootpulse", "rootecho", "rootdust", "rootring", "rootburst", "rootform", "rootmass",
    "traceline", "tracenest", "tracephase", "tracecrest", "tracebloom", "tracespark", "tracetrace", "tracelock", "traceweft", "tracenode",
    "tracewake", "tracecoil", "traceroot", "traceveil", "tracelight", "traceshift", "tracegate", "tracehorn", "tracedrift", "tracevault",
    "tracelink", "traceburn", "tracefield", "tracepulse", "traceecho", "tracedust", "tracering", "traceburst", "traceform", "tracemass",
    "veilline", "veilnest", "veilphase", "veilcrest", "veilbloom", "veilspark", "veiltrace", "veillock", "veilweft", "veilnode",
    "veilwake", "veilcoil", "veilroot", "veilveil", "veillight", "veilshift", "veilgate", "veilhorn", "veildrift", "veilvault",
    "veillink", "veilburn", "veilfield", "veilpulse", "veilecho", "veildust", "veilring", "veilburst", "veilform", "veilmass",
    "fireline", "firenest", "firephase", "firecrest", "firebloom", "firespark", "firetrace", "firelock", "fireweft", "firenode",
    "firewake", "firecoil", "fireroot", "fireveil", "firelight", "fireshift", "firegate", "firehorn", "firedrift", "firevault",
    "firelink", "fireburn", "firefield", "firepulse", "fireecho", "firedust", "firering", "fireburst", "fireform", "firemass",
    "shardline", "shardnest", "shardphase", "shardcrest", "shardbloom", "shardspark", "shardtrace", "shardlock", "shardweft", "shardnode",
    "shardwake", "shardcoil", "shardroot", "shardveil", "shardlight", "shardshift", "shardgate", "shardhorn", "sharddrift", "shardvault",
    "shardlink", "shardburn", "shardfield", "shardpulse", "shardecho", "sharddust", "shardring", "shardburst", "shardform", "shardmass",
    "dustline", "dustnest", "dustphase", "dustcrest", "dustbloom", "dustspark", "dusttrace", "dustlock", "dustweft", "dustnode",
    "dustwake", "dustcoil", "dustroot", "dustveil", "dustlight", "dustshift", "dustgate", "dusthorn", "dustdrift", "dustvault",
    "dustlink", "dustburn", "dustfield", "dustpulse", "dustecho", "dustdust", "dustring", "dustburst", "dustform", "dustmass",
    "formline", "formnest", "formphase", "formcrest", "formbloom", "formspark", "formtrace", "formlock", "formweft", "formnode",
    "formwake", "formcoil", "formroot", "formveil", "formlight", "formshift", "formgate", "formhorn", "formdrift", "formvault",
    "formlink", "formburn", "formfield", "formpulse", "formecho", "formdust", "formring", "formburst", "formform", "formmass",
    "warpline", "warpnest", "warpphase", "warpcrest", "warpbloom", "warpspark", "warptrace", "warplock", "warpweft", "warpnode",
    "warpwake", "warpcoil", "warproot", "warpveil", "warplight", "warpshift", "warpgate", "warphorn", "warpdrift", "warpvault",
    "warplink", "warpburn", "warpfield", "warppulse", "warpecho", "warpdust", "warpring", "warpburst", "warpform", "warpmass",
    "shadeline", "shadenest", "shadephase", "shadecrest", "shadebloom", "shadespark", "shadetrace", "shadelock", "shadeweft", "shadenode",
    "shadewake", "shadecoil", "shaderoot", "shadeveil", "shadelight", "shadeshift", "shadegate", "shadehorn", "shadedrift", "shadevault",
    "shadelink", "shadeburn", "shadefield", "shadepulse", "shadeecho", "shadedust", "shadering", "shadeburst", "shadeform", "shademass",
    "fractline", "fractnest", "fractphase", "fractcrest", "fractbloom", "fractspark", "fracttrace", "fractlock", "fractweft", "fractnode",
    "fractwake", "fractcoil", "fractroot", "fractveil", "fractlight", "fractshift", "fractgate", "fracthorn", "fractdrift", "fractvault",
    "fractlink", "fractburn", "fractfield", "fractpulse", "fractecho", "fractdust", "fractring", "fractburst", "fractform", "fractmass",
    "crestline", "crestnest", "crestphase", "crestcrest", "crestbloom", "crestspark", "cresttrace", "crestlock", "crestweft", "crestnode",
    "crestwake", "crestcoil", "crestroot", "crestveil", "crestlight", "crestshift", "crestgate", "cresthorn", "crestdrift", "crestvault",
    "crestlink", "crestburn", "crestfield", "crestpulse", "crestecho", "crestdust", "crestring", "crestburst", "crestform", "crestmass",
    "nestline", "nestnest", "nestphase", "nestcrest", "nestbloom", "nestspark", "nesttrace", "nestlock", "nestweft", "nestnode",
    "nestwake", "nestcoil", "nestroot", "nestveil", "nestlight", "nestshift", "nestgate", "nesthorn", "nestdrift", "nestvault",
    "nestlink", "nestburn", "nestfield", "nestpulse", "nestecho", "nestdust", "nestring", "nestburst", "nestform", "nestmass",
    "skyline", "skynest", "skyphase", "skycrest", "skybloom", "skyspark", "skytrace", "skylock", "skyweft", "skynode",
    "skywake", "skycoil", "skyroot", "skyveil", "skylight", "skyshift", "skygate", "skyhorn", "skydrift", "skyvault",
    "skylink", "skyburn", "skyfield", "skypulse", "skyecho", "skydust", "skyring", "skyburst", "skyform", "skymass",
    "orbline", "orbnest", "orbphase", "orbcrest", "orbbloom", "orbspark", "orbtrace", "orblock", "orbweft", "orbnode",
    "orbwake", "orbcoil", "orbroot", "orbveil", "orblight", "orbshift", "orbgate", "orbhorn", "orbdrift", "orbvault",
    "orblink", "orbburn", "orbfield", "orbpulse", "orbecho", "orbdust", "orbring", "orbburst", "orbform", "orbmass",
    "spiralline", "spiralnest", "spiralphase", "spiralcrest", "spiralbloom", "spiralspark", "spiraltrace", "spirallock", "spiralweft", "spiralnode",
    "spiralwake", "spiralcoil", "spiralroot", "spiralveil", "spirallight", "spiralshift", "spiralgate", "spiralhorn", "spiraldrift", "spiralvault",
    "spirallink", "spiralburn", "spiralfield", "spiralpulse", "spiralecho", "spiraldust", "spiralring", "spiralburst", "spiralform", "spiralmass",
    "threadline", "threadnest", "threadphase", "threadcrest", "threadbloom", "threadspark", "threadtrace", "threadlock", "threadweft", "threadnode",
    "threadwake", "threadcoil", "threadroot", "threadveil", "threadlight", "threadshift", "threadgate", "threadhorn", "threaddrift", "threadvault",
    "threadlink", "threadburn", "threadfield", "threadpulse", "threadecho", "threaddust", "threadring", "threadburst", "threadform", "threadmass",
    "fluxline", "fluxnest", "fluxphase", "fluxcrest", "fluxbloom", "fluxspark", "fluxtrace", "fluxlock", "fluxweft", "fluxnode",
    "fluxwake", "fluxcoil", "fluxroot", "fluxveil", "fluxlight", "fluxshift", "fluxgate", "fluxhorn", "fluxdrift", "fluxvault",
    "fluxlink", "fluxburn", "fluxfield", "fluxpulse", "fluxecho", "fluxdust", "fluxring", "fluxburst", "fluxform", "fluxmass"
]




# Base font path for glyph rendering
DEFAULT_GLYPH_FONT_PATH = "_fonts/Symbola.ttf"

# Image sizes for glyph and FFT rendering
GLYPH_IMAGE_SIZE = (512, 512)
FFT_IMAGE_SIZE = (512, 512)

GLOSSARY_SUFFIX = "_gg.json"

# Directory structure keys
GLYPH_DIR = "glyphs"
GLYPH_DB_DIR = "glyphs/dbRw"
GLYPH_FFT_DIR = "glyphs/fft"
GLYPH_FFT_RAW_DIR = "glyphs/fft_raw"
GLYPH_TOKENS_DIR = "glyphs/tokens"
GLYPH_IMG_FFT_DIR = "glyph_images/fft"
GLYPH_AUDIO_DIR = "glyphs/audio"
GLYPH_AUDIO_IMG_DIR = "glyphs/audio_img"
GLYPH_IMAGE_DIR = "glyph_images"
TOKEN_FFT_DIR = "tokens_fft"
TOKEN_FFT_IMG_DIR = "tokens_fft_img"
TOKEN_AUDIO_DIR = "tokens_audio"
INTERMODAL_DIR = "intermodal"
AVATAR_SLOTS_DIR = "avatar_slots"

# Gate names and prompt phrases
AGENCY_GATES = [
    "Continue thinking?",
    "Be spontaneous?",
    "Go deep?",
    "Be creative?",
    "Refine voice?",
    "Prioritize output?",
    "Suppress output?",
    "Question self?",
    "Recall memory?",
    "Delay response?",
    "Reveal externally?"
]