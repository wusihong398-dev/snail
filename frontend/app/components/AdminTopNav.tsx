"use client";


import {
  adminModules
} from "./menuConfig";


export default function AdminTopNav({

currentModule,

onChange

}:any){


return (

<div

style={{

display:"flex",

gap:20,

alignItems:"center"

}}

>


{

Object.keys(adminModules).map(

(key)=>(


<div

key={key}

onClick={()=>onChange(key)}

style={{

cursor:"pointer",

padding:"8px 12px",

borderRadius:6,


background:

currentModule===key

?

"#1677ff"

:

"transparent",


color:

currentModule===key

?

"#fff"

:

"#333"

}}

>

{adminModules[key].title}

</div>


)

)

}


</div>

);


}
