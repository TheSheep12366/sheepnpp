// Original RBMK-inspired props, authored for 004. Run inside Blockbench after new_project(java_block).
(function (params) {
  const id = params.id;
  const root = '/www/wwwroot/mcmoddevlop/004/prototypes/rbmk_equipment/';
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 32;
  const ctx = canvas.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  const rect = (x,y,w,h,c) => { ctx.fillStyle=c; ctx.fillRect(x,y,w,h); };
  const mint = id === 'rbmk_analog_console';
  const metal = id === 'rbmk_fuel_channel_head' || id === 'rbmk_reactor_service_hatch';
  const base = mint ? '#879f8f' : metal ? '#78848a' : '#aab3ab';
  rect(0,0,32,32,base);
  // The first quadrant is the principal panel; hardware swatches occupy the lower half.
  rect(0,0,16,16,metal ? '#6c797f' : '#34454a');
  rect(16,0,8,8,'#28373c');
  for(let y=0;y<8;y++) for(let x=0;x<8;x++) {
    const d=Math.hypot(x-3.5,y-3.5);
    if(d<3.3) rect(16+x,y,1,1,d>2.5?'#89958f':'#d9dbc8');
  }
  rect(19,2,1,3,'#414d4b'); rect(20,1,1,2,'#a37854');
  const shades=['#293b41','#596e73','#a8b7b9','#d1d8ce',base,'#79a486','#c8a24d','#a46554'];
  shades.forEach((c,i)=>rect(i*4,16,4,4,c));
  rect(16,8,16,8,base);
  for(let y=9;y<15;y++) for(let x=17;x<31;x++) {
    if((x*17+y*11)%9===0) rect(x,y,1,1,mint?'#8aa292':metal?'#7b878d':'#adb6ae');
  }
  if(id==='rbmk_analog_console') {
    rect(0,0,16,16,'#6b8578');
    for(let y=2;y<=6;y+=4) for(let x=2;x<15;x+=3) {
      rect(x,y,2,2,'#24383c'); rect(x,y,1,1,'#aabdb0');
    }
    for(let x=2;x<15;x+=3) {rect(x,11,2,2,'#b7c4ae');rect(x,10,1,2,'#3d5559');}
    rect(2,14,12,1,'#425c57');
  } else if(id==='rbmk_channel_mimic_panel') {
    rect(1,1,14,14,'#2d4146');
    // A regular channel grid interrupted by two readable bus lines, not fake text.
    for(let y=2;y<15;y+=3) for(let x=2;x<15;x+=3) rect(x,y,2,2,'#b5c1ac');
    rect(7,1,1,14,'#7b9b91');rect(1,7,14,1,'#7b9b91');
    rect(2,2,2,2,'#bf9a4b');rect(11,11,2,2,'#a56b58');
  } else if(id==='rbmk_radiation_monitor') {
    rect(1,1,14,10,'#d5d9c1');
    for(let x=3;x<14;x+=2) rect(x,2,1,x%3===0?3:2,'#677466');
    rect(8,4,1,4,'#a16648');rect(7,7,2,1,'#394f4f');
    rect(2,12,5,2,'#7aa48c');rect(9,12,5,2,'#c3a353');
  } else if(id==='rbmk_fuel_channel_head') {
    rect(1,1,14,14,'#64757c');rect(3,3,10,10,'#a2afb0');
    rect(5,5,6,6,'#485e66');rect(7,4,2,8,'#8b999b');
    for(const [x,y] of [[2,2],[12,2],[2,12],[12,12]]) rect(x,y,2,2,'#334c56');
  } else if(id==='rbmk_reactor_service_hatch') {
    rect(1,1,14,14,'#72858b');
    for(let x=2;x<15;x+=4) {rect(x,2,1,12,'#7f9297');rect(x+1,2,1,12,'#6a7d84');}
    rect(5,2,6,2,'#c8ac65');rect(6,2,4,1,'#52666c');
  } else throw new Error('Unknown prop: '+id);

  const url=canvas.toDataURL('image/png');
  const texture=new Texture({name:id+'.png',folder:'block',namespace:'sheepnpp'}).fromDataURL(url).add();
  Project.texture_width=32; Project.texture_height=32; Project.parent='minecraft:block/block';
  const cubes=[];
  const box=(name,from,to,mat='body',rotation=null,origin=null)=>{
    const cube=new Cube({name,from,to,autouv:0,box_uv:false});
    if(rotation){cube.rotation=rotation;cube.origin=origin;}
    cube.init();
    const slot={dark:0,hardware:1,steel:2,ivory:3,body:4,green:5,yellow:6,red:7};
    for(const [face,f] of Object.entries(cube.faces)) {
      f.texture=texture.uuid;
      f.uv=mat==='panel'?[0,0,16,16]:mat==='gauge'?[16,0,24,8]:mat==='body'?[16,8,32,16]:[slot[mat]*4+1,17,slot[mat]*4+2,18];
      // Graphics belong on the face, not on the sides of each meter housing.
      const topGraphic = face==='up' && (id==='rbmk_fuel_channel_head' || id==='rbmk_analog_console');
      if((mat==='panel'||mat==='gauge') && face!=='north' && !topGraphic) f.uv=[17,9,23,14];
    }
    cubes.push(cube); return cube;
  };
  Undo.initEdit({elements:[],textures:[texture],outliner:true});
  if(id==='rbmk_analog_console') {
    box('plinth',[1,0,3],[15,1,13],'dark');
    box('pedestal',[2,0.8,4],[14,9,12]);
    box('back_upright',[1.5,8,11],[14.5,14.5,14]);
    box('upper_fascia',[1,12,10.9],[15,15,13.5]);
    box('front_apron',[1,6.5,2],[15,9.7,3]);
    box('sloping_control_deck',[1.1,8,2.2],[14.9,8.6,11.4],'panel',[22.5,0,0],[8,8,7]);
    for(let i=0;i<4;i++) box('meter_'+i,[2.2+i*3.05,11.2,10.45],[4.65+i*3.05,13.65,11.3],'gauge');
    for(let i=0;i<5;i++) {
      box('switch_base_'+i,[2.4+i*2.2,9.2,3.4],[3.3+i*2.2,9.7,4.4],'dark');
      box('switch_lever_'+i,[2.65+i*2.2,9.5,3.6],[3.05+i*2.2,10.5,4.1],i===4?'red':'ivory');
    }
    box('toe_recess',[3,1.5,3.7],[13,3.8,4.2],'dark');
  } else if(id==='rbmk_channel_mimic_panel') {
    box('back_frame',[1,1,14.2],[15,15,16],'hardware');
    box('inset_gasket',[1.5,1.5,13.5],[14.5,14.5,14.8],'dark');
    box('channel_grid_screen',[2,2,13],[14,14,14.1],'panel');
    for(const [x,y] of [[1.3,1.4],[14,1.4],[1.3,14.1],[14,14.1]]) box('frame_fastener_'+x+'_'+y,[x,y,13.7],[x+.6,y+.5,14.3],'steel');
    box('lower_name_bar',[4,1.2,13.65],[12,1.7,14.3],'ivory');
  } else if(id==='rbmk_radiation_monitor') {
    box('instrument_body',[3,2,11],[13,14,16]);
    box('front_gasket',[3.4,2.4,10.6],[12.6,13.6,11.4],'dark');
    box('analog_dose_meter',[3.8,7.5,10],[12.2,13.2,11.2],'panel');
    box('selector_base',[9.6,3.2,10.4],[12,5.6,11.3],'dark');
    box('selector_knob',[10.1,3.65,10.1],[11.5,5.1,10.8],'hardware');
    for(let i=0;i<3;i++) box('speaker_louver_'+i,[4.2,3.1+i*.95,10.45],[8.4,3.5+i*.95,11.2],'hardware');
    box('status_green',[4.1,6.3,10.35],[5.4,7,11],'green');
    box('status_amber',[6,6.3,10.32],[7.3,7,11.05],'yellow');
  } else if(id==='rbmk_fuel_channel_head') {
    box('square_base_flange',[2,0,2],[14,1.5,14],'hardware');
    box('lower_pressure_body',[3,1.3,3],[13,4.5,13]);
    box('upper_channel_collar',[4,4.3,4],[12,7.5,12],'steel');
    box('top_sealing_lid',[5,7.2,5],[11,8,11],'panel');
    box('lug_a',[2,1.8,6],[4,3,10],'steel');box('lug_b',[12,1.82,6.05],[14,3.02,10.05],'steel');
    box('lug_c',[6,1.84,2],[10,3.04,4],'steel');box('lug_d',[6.05,1.86,12],[10.05,3.06,14],'steel');
    for(const [x,z] of [[3.2,3.2],[11.7,3.2],[3.2,11.7],[11.7,11.7]]) box('flange_bolt_'+x+'_'+z,[x,1.35,z],[x+1.1,2.2,z+1.1],'ivory');
    box('lock_bar',[6,6.3,3.75],[10,7,4.4],'dark');
  } else {
    box('outer_frame',[1,1,14.2],[15,15,16],'hardware');
    box('door_gasket',[1.65,1.65,13.9],[14.35,14.35,14.7],'dark');
    box('ribbed_door',[2,2,13.6],[14,14,14.8],'panel');
    box('locking_bar_a',[3,3,13.2],[3.6,13,14.1],'steel');
    box('locking_bar_b',[12.4,3.1,13.25],[13,12.9,14.15],'steel');
    box('wheel_hub',[7,7,12],[9,9,14.2],'hardware');
    box('wheel_top',[5.2,10.4,12.45],[10.8,11.2,13.3],'steel');
    box('wheel_bottom',[5.25,4.8,12.47],[10.75,5.6,13.35],'steel');
    box('wheel_edge_a',[4.8,5.3,12.5],[5.6,10.7,13.4],'steel');
    box('wheel_edge_b',[10.4,5.35,12.52],[11.2,10.65,13.45],'steel');
    box('wheel_spoke_h',[5.4,7.7,12.8],[10.6,8.3,13.7],'hardware');
    box('wheel_spoke_v',[7.7,5.4,12.85],[8.3,10.6,13.75],'hardware');
    box('hinge_a',[1.5,10.9,13.4],[2.5,13.1,15],'hardware');
    box('hinge_b',[1.55,2.9,13.45],[2.55,5.1,15.05],'hardware');
  }
  Undo.finishEdit('Build '+id);
  Canvas.updateAll();
  Blockbench.writeFile(root+id+'.png',{content:url,savetype:'image'});
  const compiled=Codecs.java_block.compile();
  const model=typeof compiled==='string'?JSON.parse(compiled):compiled;
  delete model.format_version;
  model.parent='minecraft:block/block';
  model.textures.particle='minecraft:block/gray_concrete';
  Blockbench.writeFile(root+id+'.json',{content:JSON.stringify(model,null,2),savetype:'text'});
  return {id,elements:cubes.length,texture:[32,32]};
})
