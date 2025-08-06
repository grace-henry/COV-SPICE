
def initialize_mutations():
    mutations = []
    mutation_insert_r = "inserting one resistance element"
    mutations.append(mutation_insert_r)
    mutation_insert_c = "inserting one capacitor element"
    mutations.append(mutation_insert_c)
    mutation_insert_l = "inserting one inductor element"
    mutations.append(mutation_insert_l)
    mutation_insert_i = "inserting one current source element"
    mutations.append(mutation_insert_i)
    mutation_insert_v = "inserting one voltage source element"
    mutations.append(mutation_insert_v)
    mutation_insert_d = "inserting one diode element"
    mutations.append(mutation_insert_d)
    mutation_insert_q1 = "inserting one NPN transistor element"
    mutations.append(mutation_insert_q1)
    mutation_insert_q2 = "inserting one PNP transistor element"
    mutations.append(mutation_insert_q2)
    mutation_insert_j1 = "inserting one NJF transistor element"
    mutations.append(mutation_insert_j1)
    mutation_insert_j2 = "inserting one PJF transistor element"
    mutations.append(mutation_insert_j2)
    mutation_insert_m1 = "inserting one NMOS transistor element"
    mutations.append(mutation_insert_m1)
    mutation_insert_m2 = "inserting one PMOS transistor element"
    mutations.append(mutation_insert_m2)
    mutation_insert_m3 = "inserting one VDMOS transistor element"
    mutations.append(mutation_insert_m3)
    mutation_insert_s = "inserting one voltage controlled switch element"
    mutations.append(mutation_insert_s)
    mutation_insert_w = "inserting one current controlled switch element"
    mutations.append(mutation_insert_w)
    mutation_insert_sub_circuit = "inserting one subcircuit"
    mutations.append(mutation_insert_sub_circuit)
    mutation_insert_func = "inserting one function block"
    mutations.append(mutation_insert_func)
    mutation_insert_param = "inserting one param line"
    mutations.append(mutation_insert_param)
    mutation_insert_if = "inserting one IF control block"
    mutations.append(mutation_insert_if)
    mutation_change_to_dc = "changing the analysis type to DC analysis"
    mutations.append(mutation_change_to_dc)
    mutation_change_to_ac = "changing the analysis type to AC Small-Signal analysis"
    mutations.append(mutation_change_to_ac)
    mutation_change_to_tran = "changing the analysis type to Transient analysis"
    mutations.append(mutation_change_to_tran)
    mutation_change_to_pz = "changing the analysis type to Pole-Zero analysis"
    mutations.append(mutation_change_to_pz)
    mutation_change_to_noise = "changing the analysis type to Noise analysis"
    mutations.append(mutation_change_to_noise)
    # mutation_delete = "deleting one element"
    # mutations.append(mutation_delete)
    return mutations


def initialize_forms():
    forms = []
    # form_of_r = "The general form of resistance element is '''RXXX n+ n- <r=>value <ac=val> <m=val> <scale=val> <temp=val> <dtemp=val> <tc1=val> <tc2=val> <noisy=0|1>'''."
    form_of_r = "The general form of resistance element is '''R<name> <+ node> <- node> [model name] <value> [L=<length>] [W=<width>]'''."
    forms.append(form_of_r)
    # form_of_c = "The general form of capacitor element is '''CXXX n+ n- <value> <mname> <m=val> <scale=val> <temp=val> <dtemp=val> <tc1=val> <tc2=val> <ic=init_condition>'''."
    form_of_c = "The general form of capacitor element is '''C<name> <+ node> <- node> [model name] <value> [IC=<initial value>]'''."
    forms.append(form_of_c)
    form_of_l = "The general form of inductor element is '''L<name> <+ node> <- node> [model name] <value> [IC=<initial value>]'''."
    forms.append(form_of_l)
    # form_of_i = "The general form of current source element is '''IYYY N+ N- <<DC> DC/TRAN VALUE> <AC <ACMAG <ACPHASE>>> <DISTOF1 <F1MAG <F1PHASE>>> <DISTOF2 <F2MAG <F2PHASE>>>'''."
    form_of_i = "The general form of current source element is '''I<name> <+ node> <- node> [[DC] <value>] [AC [magnitude value [phase value] ] ] [transient specification]'''."
    forms.append(form_of_i)
    # form_of_v = "The general form of voltage source element is '''VXXX N+ N- <<DC> DC/TRAN VALUE> <AC <ACMAG <ACPHASE>>> <DISTOF1 <F1MAG <F1PHASE>>> <DISTOF2 <F2MAG <F2PHASE>>>'''."
    form_of_v = "The general form of voltage source element is '''V<name> <+ node> <- node> [[DC] <value>] [AC [magnitude value [phase value] ] ] [transient specification]'''."
    forms.append(form_of_v)
    # form_of_d = "The general form of diode element is '''DXXX n+ n- mname <area=val> <m=val> <pj=val> <off> <ic=vd> <temp=val> <dtemp=val> <lm=val> <wm=val> <lp=val> <wp=val>'''. The general form of diode model is '''.model D type (pname1=pval1 pname2=pval2 ... )'''."
    form_of_d = (
        "The general form of diode element is '''D<name> <anode node> <cathode node> <model name> [area value]'''. "
        "The general form of diode model is '''.model <model name> D (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_d)

    # form_of_q1 = "The general form of NPN transistor element is '''QXXX nc nb ne <ns> <tj> mname <area=val> <areac=val> <areab=val> <m=val> <off> <ic=vbe,vce> <temp=val> <dtemp=val>'''. The general form of NPN model is '''.model mname NPN (pname1=pval1 pname2=pval2 ... )'''."
    form_of_q1 = (
        "The general form of NPN transistor element is '''Q<name> <collector node> <base node> <emitter node> "
        "[substrate node] <model name> [area value] [optional parameters]'''. "
        "The general form of NPN model is '''.model <model name> NPN (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_q1)

    # form_of_q2 = "The general form of PNP transistor element is '''QXXX nc nb ne <ns> <tj> mname <area=val> <areac=val> <areab=val> <m=val> <off> <ic=vbe,vce> <temp=val> <dtemp=val>'''. The general form of PNP model is '''.model mname PNP (pname1=pval1 pname2=pval2 ... )'''."
    form_of_q2 = (
        "The general form of PNP transistor element is '''Q<name> <collector node> <base node> <emitter node> "
        "[substrate node] <model name> [area value] [optional parameters]'''. "
        "The general form of PNP model is '''.model <model name> PNP (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_q2)

    # form_of_j1 = "The general form of NJF element is '''JXXX nd ng ns mname <area> <off> <ic=vds, vgs> <temp=t>'''. The general form of NJF model is '''.model mname NJF (pname1=pval1 pname2=pval2 ... )'''."
    # forms.append(form_of_j1)
    # form_of_j2 = "The general form of PJF element is '''JXXX nd ng ns mname <area> <off> <ic=vds, vgs> <temp=t>'''. The general form of PJF model is '''.model mname PJF (pname1=pval1 pname2=pval2 ... )'''."
    # forms.append(form_of_j2)
    form_of_j1 = (
        "The general form of NJF element is '''J<name> <drain node> <gate node> <source node> <model name> [area value]'''. "
        "The general form of NJF model is '''.model <model name> NJF (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_j1)

    form_of_j2 = (
        "The general form of PJF element is '''J<name> <drain node> <gate node> <source node> <model name> [area value]'''. "
        "The general form of PJF model is '''.model <model name> PJF (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_j2)

    # form_of_m1 = "The general form of NMOS element is '''MXXX nd ng ns nb mname <m=val> <l=val> <w=val> <ad=val> <as=val> <pd=val> <ps=val> <nrd=val> <nrs=val> <off> <ic=vds, vgs, vbs> <temp=t>'''. The general form of NMOS model is '''.model mname NMOS (pname1=pval1 pname2=pval2 ... )'''."
    # forms.append(form_of_m1)
    # form_of_m2 = "The general form of PMOS element is '''MXXX nd ng ns nb mname <m=val> <l=val> <w=val> <ad=val> <as=val> <pd=val> <ps=val> <nrd=val> <nrs=val> <off> <ic=vds, vgs, vbs> <temp=t>'''. The general form of PMOS model is '''.model mname PMOS (pname1=pval1 pname2=pval2 ... )'''."
    # forms.append(form_of_m2)
    # form_of_m3 = "The general form of VDMOS element is '''MXXX nd ng ns mname <m=val> <temp=t> <dtemp=t>'''. The general form of VDMOS model is '''.model mname VDMOS (pname1=pval1 pname2=pval2 ... )'''."
    # forms.append(form_of_m3)
    form_of_m1 = (
        "The general form of NMOS element is '''M<name> <drain node> <gate node> <source node> <bulk node> "
        "[SOI node(s)] <model name> [common model parameter]*'''. "
        "The general form of NMOS model is '''.model <model name> NMOS (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_m1)

    form_of_m2 = (
        "The general form of PMOS element is '''M<name> <drain node> <gate node> <source node> <bulk node> "
        "[SOI node(s)] <model name> [common model parameter]*'''. "
        "The general form of PMOS model is '''.model <model name> PMOS (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_m2)

    form_of_m3 = (
        "The general form of VDMOS element is '''M<name> <drain node> <gate node> <source node> <model name> "
        "[common model parameter]*'''. "
        "The general form of VDMOS model is '''.model <model name> VDMOS (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_m3)

    # form_of_s = "The general form of voltage controlled switch element is '''SXXX N+ N- NC+ NC- MODEL <ON> <OFF>'''. The general form of voltage controlled switch model is '''.model mname SW (pname1=pval1 pname2=pval2 ... )'''."
    # forms.append(form_of_s)
    form_of_s = (
        "The general form of Voltage Controlled Switch element is '''S<name> <+ switch node> <- switch node> "
        "<+ controlling node> <- controlling node> <model name>'''. "
        "The general form of Voltage Controlled Switch model is '''.model <model name> SW (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_s)

    # form_of_w = "The general form of current controlled switch element is '''WYYY N+ N- VNAM MODEL <ON> <OFF>'''. The general form of current controlled switch model is '''.model mname CSW (pname1=pval1 pname2=pval2 ... )'''."
    # forms.append(form_of_w)

    form_of_w = (
        "The general form of Current Controlled Switch element is '''W<name> <+ switch node> <- switch node> "
        "<controlling V device name> <model name>'''. "
        "The general form of Current Controlled Switch model is '''.model <model name> CSW (parameter1=value1 parameter2=value2 ...)'''."
    )
    forms.append(form_of_w)

    # form_of_x = "The general form of subcircuit is '''XYYYYYYY N1 <N2 N3 ... > SUBNAM'''. The general form of current controlled switch model is '''.SUBCKT subnam N1 <N2 N3 ... > \n ... \n .ENDS <SUBNAM>'''."
    # forms.append(form_of_x)
    form_of_x = (
        "The general form of subcircuit element is '''X<name> [node]* <subcircuit name> "
        "[PARAMS: [<name>=<value>]*]'''. "
        "The general form of subcircuit definition is '''.SUBCKT <subcircuit name> [node]* "
        "[PARAMS: [<name>=<value>]*] \n ... \n .ENDS <subcircuit name>'''."
    )
    forms.append(form_of_x)

    # form_of_func = "The general form of function block is '''.func <ident> { <expr> }''' or '''.func <ident> = { <expr> }'''."
    # forms.append(form_of_func)
    # form_of_parm = "The general form of parm line is '''.param <ident> = <expr> <ident> = <expr> ...'''."
    # forms.append(form_of_parm)
    # form_of_if = "The general form of if control block is '''.if ( boolean expression ) \n ... \n .elseif ( boolean expression ) \n ... \n .else \n ... \n .endif'''."
    # forms.append(form_of_if)
    # form_of_dc = "The general form of DC analysis is '''.dc srcnam vstart vstop vincr [src2 start2 stop2 incr2]'''."
    # forms.append(form_of_dc)
    # form_of_ac = "The general forms of AC Small-Signal analysis are '''.ac dec nd fstart fstop''' or '''.ac oct no fstart fstop''' or '''.ac lin np fstart fstop'''."
    # forms.append(form_of_ac)
    # form_of_tran = "The general form of Transient analysis is '''.tran tstep tstop <tstart <tmax>> <uic>'''."
    # forms.append(form_of_tran)
    # form_of_pz = "The general forms of Pole-Zero analysis are '''.pz node1 node2 node3 node4 cur pol''' or '''.pz node1 node2 node3 node4 cur zer''' or '''.pz node1 node2 node3 node4 cur pz''' or '''.pz node1 node2 node3 node4 vol pol''' or '''.pz node1 node2 node3 node4 vol zer'''  or '''.pz node1 node2 node3 node4 vol pz'''."
    # forms.append(form_of_pz)
    # form_of_noise = "The general form of Noise analysis is '''.noise v ( output <, ref >) src (dec | lin | oct ) pts fstart fstop < pts_per_summary >'''."
    # forms.append(form_of_noise)


    # Function block
    form_of_func = "The general form of function block is '''.FUNC function_name(parameter_list) { expression }'''."
    forms.append(form_of_func)

    # Parameter definition
    form_of_parm = "The general form of parameter definition is '''.PARAM <ident> = <expr> [<ident> = <expr> ...]'''."
    forms.append(form_of_parm)

    # Conditional control block
    form_of_if = "The general form of conditional control block is '''.IF ( boolean expression ) \n ... \n .ELSEIF ( boolean expression ) \n ... \n .ELSE \n ... \n .ENDIF'''."
    forms.append(form_of_if)

    # DC analysis
    form_of_dc = "The general form of DC analysis is '''.DC <source> <vstart> <vstop> <vincr> [<source2> <start2> <stop2> <incr2>]'''."
    forms.append(form_of_dc)

    # AC analysis
    form_of_ac = "The general form of AC Small-Signal analysis is '''.AC <DEC | OCT | LIN> <numpoints> <fstart> <fstop>'''."
    forms.append(form_of_ac)

    # Transient analysis
    form_of_tran = "The general form of Transient analysis is '''.TRAN <tstep> <tstop> [<tstart>] [<tmax>] [UIC]'''."
    forms.append(form_of_tran)

    # Pole-Zero analysis
    form_of_pz = "The general form of Pole-Zero analysis is '''.PZ <node1> <node2> <node3> <node4> <cur | vol> <pol | zer | pz>'''."
    forms.append(form_of_pz)

    # Noise analysis
    form_of_noise = "The general form of Noise analysis is '''.NOISE <v(output) [ref]> <source> <DEC | LIN | OCT> <points> <fstart> <fstop> [<points_per_summary>]'''."
    forms.append(form_of_noise)

    return forms
