NSLog_ = dlsym(RTLD_DEFAULT, "NSLog");
WCDLog = function() { var types = 'v', args = [], count = arguments.length; for (var i = 0; i != count; ++i) { types += '@'; args.push(arguments[i]); } new Functor(NSLog_, types).apply(null, args); }

_method_copyReturnType=new Functor(dlsym(RTLD_DEFAULT,"method_copyReturnType"),"*^{objc_method=}");
_method_copyArgumentType=new Functor(dlsym(RTLD_DEFAULT,"method_copyArgumentType"),"*^{objc_method=}I");
__sysctlbyname=new Functor(dlsym(-2,"sysctlbyname"),"v*^?^i^?i");

function is64Bit(){
	
	size=new int;
	__sysctlbyname("hw.cpu64bit_capable",NULL,size,NULL,0);
	is64Bit=new BOOL;
	__sysctlbyname("hw.cpu64bit_capable",is64Bit,size,NULL,0);
	return *is64Bit;
	 

}


NSNotFound=is64Bit() ? 9.2233720368547758e+18 : 2147483647;

function commonTypes(type){

	isPointer=NO;
	if ([type containsSubstring:@"^"]){
		isPointer=YES;
		type=[type stringByReplacingOccurrencesOfString:@"^" withString:""];
	}
	
	switch (type.toString()){
	
		case "d": type = "double"; break;
		case "i": type = "int"; break;
		case "f": type = "float"; break;
		case "c": type = "BOOL"; break;
		case "s": type = "short"; break;
		case "I": type = "unsigned"; break;
		case "l": type = "long"; break;
		case "q": type = "long long"; break;
		case "L": type = "unsigned long"; break;
		case "C": type = "unsigned char"; break;
		case "S": type = "unsigned short"; break;
		case "Q": type = "unsigned long long"; break;
		case "B": type = "BOOL"; break; //replacing  _Bool , change it here if you wish
		case "v": type = "void"; break;
		case "*": type = "char*"; break;
		case ":": type = "SEL"; break;
		case "#": type = "Class"; break;
		case "@": type = "id"; break;
		case "@?": type = "id"; break;
		case "Vv": type = "void"; break;
		case "rv": type = "const void*"; break;
		default: type = type;
	
	}
	
	return isPointer ? type.toString()+"*" : type.toString();


}



function getProtocolLines(protocol){
	
	var protocolsMethodsString="";
	currentProtocol=protocol;
			
			protocolName=protocol_getName(currentProtocol);
			protocolsMethodsString=protocolsMethodsString.toString()+"\n@protocol "+protocolName.toString()+"\n";
			
			protPropertiesString="";
			protPropertiesCount=new int;
			protPropertyList=protocol_copyPropertyList(currentProtocol,protPropertiesCount);
			for (xi=0; xi<*protPropertiesCount; xi++){
		
				propname=property_getName(protPropertyList[xi]);
				attrs=property_getAttributes(protPropertyList[xi]);
				newString=propertyLineGenerator(attrs,propname).toString();
				if (![protPropertiesString containsSubstring:newString]){
					protPropertiesString=protPropertiesString.toString()+newString.toString();
				}
				
				
			}
			protocolsMethodsString=protocolsMethodsString.toString()+protPropertiesString;
			free(protPropertyList);
			
			for (acase=0; acase<5; acase++){
			
				protocolMethodsCount=new int;
				isRequiredMethod=acase<2 ? NO : YES;
				isInstanceMethod=(acase==0 || acase==2) ? NO : YES;
								
				protMeths=protocol_copyMethodDescriptionList(currentProtocol, isRequiredMethod, isInstanceMethod, protocolMethodsCount);
				for (gg=0; gg<*protocolMethodsCount; gg++){
					if (acase<2 && ![[NSString stringWithString:protocolsMethodsString] containsSubstring:@"@optional"]){
						protocolsMethodsString=protocolsMethodsString.toString()+"@optional\n";
					}
					if (acase>1 && ![[NSString stringWithString:protocolsMethodsString] containsSubstring:@"@required"]){
						protocolsMethodsString=protocolsMethodsString.toString()+"@required\n";
					}
					startSign=isInstanceMethod==NO ? "+" : "-";
					protSelector=protMeths[gg][0].toString();
					protTypes=protMeths[gg][1];

					methodSign=[NSMethodSignature signatureWithObjCTypes:protTypes];
					returnType=constructTypeAndName(commonTypes([methodSign methodReturnType].toString()),"",0);

					finString="";
					if ([methodSign numberOfArguments]>2){
						selectorsArray=[[NSString stringWithString:protSelector] componentsSeparatedByString:@":"];
						for (i=2; i<[methodSign numberOfArguments]; i++){
							ad=i-2;
							argCount=ad+1;

							finString=finString.toString()+selectorsArray[ad].toString()+":("+constructTypeAndName(commonTypes([methodSign getArgumentTypeAtIndex:i].toString()),"",0).toString()+")"+"arg"+argCount.toString()+" ";
					
						}
						finString=[finString substringToIndex:finString.length-1];
					}
					else{
						finString=protSelector.toString();
		
					}
				
					finString=finString.toString()+";";
					protocolsMethodsString=protocolsMethodsString.toString()+startSign.toString()+"("+returnType.toString()+")"+finString.toString()+"\n";		
				}
				free(protMeths);
			}
			return protocolsMethodsString.toString()+"@end\n";

}

function constructTypeAndName(aType,IvarName,isIvar){

	//NSNotFound=2147483647;
	space=isIvar ? " " : "";
	compareString1=[NSString stringWithString:aType];
	compareString2=[[[NSString stringWithString:aType] stringByReplacingOccurrencesOfString:"^" withString:""] stringByAppendingString:@"*"];
	
	if (![[NSString stringWithString:commonTypes(aType)] isEqual:compareString1] && ![[NSString stringWithString:commonTypes(aType)] isEqual:compareString2]){
		
		return commonTypes(aType).toString()+" "+IvarName.toString();
	}

	charSet=[NSCharacterSet characterSetWithCharactersInString:"@^\"{}="];
	structCharSet=[NSCharacterSet characterSetWithCharactersInString:"?:{}="];
	
	if ([aType rangeOfString:"]"].location!=NSNotFound && [aType rangeOfString:"^{"].location==NSNotFound){
		
		

		
		aType=[aType stringByRemovingCharactersFromSet: [NSCharacterSet punctuationCharacterSet ]];
		arrayCount=[[aType copy] stringByRemovingCharactersFromSet: [NSCharacterSet letterCharacterSet ]];
		arrayType=[aType stringByRemovingCharactersFromSet: [NSCharacterSet decimalDigitCharacterSet ]];
		return commonTypes(arrayType).toString()+"["+arrayCount.toString()+"]"+space+IvarName.toString();
			
	}

	if ([aType rangeOfString:"{?"].location!=NSNotFound && [aType rangeOfString:"{?"].length>0 && isIvar){

		aType=[aType stringByRemovingCharactersFromSet:structCharSet];
		structValues=[aType componentsSeparatedByString:@"\""];
		structValues =[NSMutableArray arrayWithArray:structValues ];
		firstEntry=[structValues removeObjectAtIndex:0];
		[structValues removeObject:firstEntry];
		newString=[NSString stringWithString:"struct {\n"];
		namesArray=[NSMutableArray array];
		typesArray=[NSMutableArray array];
		
		for  (d=0; d<[structValues count] ; d++){
			
			if ((d % 2)==0){
				[namesArray addObject:structValues[d]];
			}
			else{
				[typesArray addObject:structValues[d]];
			}
		}

		for (e=0; e<[typesArray count]; e++){
			newString=newString.toString()+"\t\t"+constructTypeAndName(typesArray[e],namesArray[e],0).toString()+";\n";
		}
		return newString.toString()+"\t} "+IvarName.toString();
	
	}
	
	if ([aType rangeOfString:"{"].location!=NSNotFound && [aType rangeOfString:"{"].length>0){

		returnValue="struct ";
		range=[aType rangeOfString:@"="];
	
		if ([aType containsSubstring:@"^{?="]){
	
			aStruct=aType;
			structString="";
			someType="";
			aStruct=[NSString stringWithString:aStruct];
			aStruct=[aStruct stringByReplacingOccurrencesOfString:@"^{?=" withString:""];
			aStruct=[aStruct stringByReplacingOccurrencesOfString:@"}" withString:""];
		
			for (var f=0; f<[aStruct.toString() length]; f++){
				currentLetter=[aStruct substringWithRange:[f,1]];
				someType=constructTypeAndName(currentLetter,"",0);
				someType=[someType stringByRemovingWhitespace];
				structString=structString.toString()+"\t"+someType.toString()+" value"+(f+1).toString()+";\n";
			}
	
			structName="WCStruct_"+aStruct.toString();
	
			if (![structsString containsSubstring:structName]){
				structString="typedef struct{\n"+structString.toString();
				structString=structString.toString()+"} "+structName.toString()+";\n\n";
				structsString=structsString.toString()+structString.toString();
			}
		
			structName=structName.toString()+"*";
			
			return structName+" "+IvarName.toString();
		}
		aType=[aType stringByReplacingCharactersInRange:[range.location,aType.toString().length-range.location] withString:"" ];
		returnValue=returnValue.toString()+[aType stringByRemovingCharactersFromSet:structCharSet].toString();
		if ([returnValue containsSubstring:@"GSEvent"] || [returnValue containsSubstring:@"CTCall"]){
			returnValue=[returnValue stringByReplacingOccurrencesOfString:"__" withString:""];
			returnValue=[returnValue stringByReplacingOccurrencesOfString:"struct " withString:""];
			returnValue=[returnValue stringByReplacingOccurrencesOfString:"^" withString:""];
			returnValue=[returnValue stringByAppendingString:@"Ref"];
			
		}
		if ([returnValue containsSubstring:@"NSZone"]){
			returnValue="NSZone*";
		}
				
		if ([returnValue containsSubstring:@"CGPoint"] || [returnValue containsSubstring:@"CGRect"]  || [returnValue containsSubstring:@"CGSize"] ){
			returnValue=[returnValue stringByReplacingOccurrencesOfString:@"struct " withString:@""];
		}
		return commonTypes(returnValue).toString()+space+IvarName.toString();
	}
	
	
	if ([aType rangeOfString:@"^"].location!=NSNotFound && [aType rangeOfString:@"^"].length>0){
		
		range=[aType rangeOfString:"^" options: NULL range: [2,aType.toString().length-2]];
		if (range.length>0){
			aType=[aType stringByReplacingCharactersInRange:[range.location-1,aType.toString().length-range.location+1] withString:"" ];
		}
		aType=[aType stringByRemovingCharactersFromSet:charSet];
		//aType=[aType stringByReplacingOccurrencesOfString:@"__" withString:""];
		return aType.toString()+"* "+IvarName.toString();

	}
	

	
	if ([aType rangeOfString:@"@\""].location!=NSNotFound && [aType rangeOfString:@"@\""].length>0){
		if ([aType rangeOfString:"<"].location==2){
			aType="id"+aType.toString();
			return [aType stringByRemovingCharactersFromSet:charSet].toString()+" "+IvarName.toString();
		}
		
		strippedString=[aType stringByRemovingCharactersFromSet:charSet];
		return strippedString.toString()+ "* "+IvarName.toString();
		
	}	
	
	if ([aType rangeOfString:@"b"].location!=NSNotFound && [aType rangeOfString:@"b"].length>0 && [aType rangeOfString:":{"].length<1){
		string=[aType stringByReplacingOccurrencesOfString:@"b" withString:""];
		return "unsigned int "+IvarName.toString()+":"+string.toString();
	}
	
	return aType.toString() + space + IvarName.toString();
 
}



function propertyLineGenerator(attributes,name){
	
	parSet=[NSCharacterSet characterSetWithCharactersInString:@"()"];
	attributes=[attributes stringByRemovingCharactersFromSet:parSet];
	attrArr=[attributes componentsSeparatedByString:@","];
	
		type=attrArr[0];
		type=[type stringByReplacingCharactersInRange:[0,1] withString:""];
		type=constructTypeAndName(type,"",0);
		type=[type stringByRemovingWhitespace];
		attrArr=[NSMutableArray arrayWithArray:attrArr];
		[attrArr removeObjectAtIndex:0];
		
		propertyString="@property ";
		
		newPropsArray=[NSMutableArray array];
		synthesize=[NSString stringWithString:""];
		for each (attr in attrArr){
		
			vToClear=nil;		
			
			if ([attr rangeOfString:@"V_"].location==0){
				vToClear=attr;
				attr=[attr stringByReplacingCharactersInRange:[0,2] withString:""];
				synthesize="\t\t\t\t//@synthesize "+attr.toString()+"=_"+attr.toString()+" - In the implementation block";
			}
			
			if ([attr.toString() length]==1){
				
				switch (attr.toString()){
					case "R" : translatedProperty = "readonly"; 
					case "C" : translatedProperty = "copy"; break;
					case "&" : translatedProperty = "retain"; break;
					case "N" : translatedProperty = "nonatomic"; break;
					case "D" : translatedProperty = "@dynamic"; break;
					case "W" : translatedProperty = "__weak"; break;
					case "P" : translatedProperty = "t<encoding>"; break;
					default: translatedProperty = attr;
				}
				
				[newPropsArray addObject:translatedProperty];
			}
			
			if ([attr rangeOfString:@"G"].location==0){
				attr=[attr stringByReplacingCharactersInRange:[0,1] withString:""];
				attr="getter="+attr.toString();
				[newPropsArray addObject:attr];
			}
			
			if ([attr rangeOfString:@"S"].location==0){
				attr=[attr stringByReplacingCharactersInRange:[0,1] withString:""];
				attr="setter="+attr.toString();
				[newPropsArray addObject:attr];
			}
			
		}
		
		if ([newPropsArray containsObject:@"nonatomic"] && ![newPropsArray containsObject:@"assign"] && ![newPropsArray containsObject:@"readonly"] && ![newPropsArray containsObject:@"copy"] && ![newPropsArray containsObject:@"retain"]){
			[newPropsArray addObject:@"assign"];
		}
		
		newPropsArray=[newPropsArray reversedArray];
			
		rebuiltString=[newPropsArray componentsJoinedByString:","];
		attrString=newPropsArray.length>0 ? "("+rebuiltString.toString()+")" : "(assign)";
		
		propertyString=propertyString.toString()+attrString.toString()+" "+type.toString()+" "+name.toString()+"; "+synthesize.toString()+"\n";		
		return propertyString;

}

function methodLinesGenerator(methodList,methodsCount,isClassMethod){

	methodLines="";
	
	for (n=0; n<*methodsCount;n++){
		method=methodList[n];
		methodName=method_getName(method);
		if (methodName==".cxx_destruct"){
			continue;
		}
	 	returnType=_method_copyReturnType(method);
		returnType=[constructTypeAndName(returnType.toString(),[NSString stringWithString:@""],0).toString() stringByRemovingWhitespace];
		
	 	argNum=method_getNumberOfArguments(method);
		methodBrokenDown=[methodName.toString() componentsSeparatedByString:@":"];

		methodString=[NSString stringWithString:""];

		if ([methodBrokenDown count]>1){
			for (x=0; x<[methodBrokenDown count]-1; x++){
				anIndex=x+2;
				argumentType=_method_copyArgumentType(method,anIndex);
				var hadType=YES;
				if (!argumentType){
					hadType=NO;
					argumentType="id";
				}

				typeName=constructTypeAndName(argumentType.toString(),[NSString stringWithString:""],0);

				//if (hadType){
					//free(argumentType); //cannot free since its a *
				//}
				typeName=[typeName substringToIndex:typeName.toString().length-1];
				
				methodString=methodString.toString()+methodBrokenDown[x].toString()+":("+typeName.toString()+")arg"+(x+1)+" ";
				
			}
			methodString=[methodString substringToIndex:methodString.length-1];
		}
		else{
			methodString=methodName;
		}

		symbol=isClassMethod ? "+" : "-"; symbol=[NSString stringWithString:symbol.toString()];
		newMethod=symbol.toString()+"("+returnType.toString()+")"+methodString.toString()+";\n";
		cappedMethod=[[NSString stringWithString:methodName.toString()] capitalizedString];
		setterMethod="set"+cappedMethod.toString();
		//free(returnType);
		
		if (![methodsArray containsObject:newMethod.toString()] && ![propertiesString containsSubstring:methodName.toString()] && ![methodsString containsSubstring:setterMethod.toString()]){
			[methodsArray addObject:newMethod];
			methodLines=methodLines.toString()+newMethod.toString();
		}

		
	}
	return methodLines;


}

function weak_classdump(classname,alsoDumpSuperclasses,outputdir){
	
	//[[NSString stringWithString:classname.toString()] writeToFile:"/tmp/LASTCLASS" atomically:YES];
	//NSLog(@"weak_classdump: Dumping class %@",classname);
	if (!classname){
		return "Cannot find class";
	}
	
	if (typeof(alsoDumpSuperclasses) == 'undefined' || !alsoDumpSuperclasses){
		alsoDumpSuperclasses=0;
	}

	
	structsString="";
	interfaceString="";
	version = [NSProcessInfo processInfo ].operatingSystemVersionString;
	loc=[NSLocale localeWithLocaleIdentifier: "en-us"];
	date=[NSDate.date descriptionWithLocale: loc];
	classString = "/*\n * This header is generated by weak_classdump 0.2\n * on "+date.toString()+"\n * Operating System: "+version.toString()+"\n * weak_classdump is Freeware by Elias Limneos.\n *\n */\n\n";
	if ( [[classname description] containsSubstring:@"<Protocol:"]){
		
		classString=classString.toString()+getProtocolLines(classname).toString();
		
		if (typeof(outputdir) == 'undefined'){
			outputdir = "/tmp";
		}
	
		if (typeof(alsoDumpSuperclasses) == 'string'){
			outputdir=alsoDumpSuperclasses;
		}
	
	
		outputdir=outputdir.toString()+"/";
		
		if (![NSFileManager.defaultManager fileExistsAtPath:outputdir]){
			try{
				[NSFileManager.defaultManager createDirectoryAtPath:outputdir withIntermediateDirectories:YES attributes:nil error:nil];
			}catch(e){}
		}
	
		classString = [NSString stringWithString:classString ]; 
		if ([classString writeToFile:outputdir.toString()+protocol_getName(classname).toString()+".h" atomically:YES]){
			return "Wrote /PROTOCOL/ header file to "+outputdir.toString()+protocol_getName(classname).toString()+".h";
		}
		else {
			NSSearchPathForDirectoriesInDomains=new Functor(dlsym(RTLD_DEFAULT,"NSSearchPathForDirectoriesInDomains"),"@ccc");
			writeableDir=NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
			writeableDir=writeableDir[0];
			return "Failed to write to "+outputdir.toString()+protocol_getName(classname).toString()+".h - Check file path and permissions? Suggested writeable directory: "+writeableDir.toString();
		}
	
	}


	methodsArray=[NSMutableArray array];
	propertiesString=@"";
	methodsString=@"";
	ivarsString=@"";
	classMethodsString=@"";

	startingClassname=classname;
	superclass=classname.superclass;
	
	protocolsCount=new int;
	protocolArray=class_copyProtocolList(classname,protocolsCount);
	
	protocolsMethodsString=classString;
	var protocolName;
	allProtocols="";
	if (*protocolsCount>0){
		for (iter=0; iter<*protocolsCount; iter++){		
			if (class_conformsToProtocol(classname,protocolArray[iter])){
				protocolName=protocol_getName(protocolArray[iter]);
				protocolsMethodsString=protocolsMethodsString.toString()+getProtocolLines(protocolArray[iter]).toString();
			}
			
			protocolsMethodsString = [NSString stringWithString:protocolsMethodsString ]; 
			
			classString=classString.toString()+"#import <"+protocolName.toString()+".h>\n";
			
			if (typeof(outputdir)=="undefined" ||  outputdir==null){
				outputdir="/tmp";
			}
			lastChar=[outputdir.toString() substringFromIndex:outputdir.toString().length-1];
			if (![lastChar isEqual:@"/"]){
				outputdir=outputdir+"/";
			}
			allProtocols=allProtocols.toString()+", "+outputdir.toString()+protocolName.toString()+".h";
			if ([protocolsMethodsString writeToFile:outputdir.toString()+protocolName.toString()+".h" atomically:YES]){
				//NSLog(@"Found Protocol %@, wrote to %@%@.h",protocolName,outputdir,protocolName);
			}
		}	
	}

	
	protocolsString="";
	if (*protocolsCount>0){
		protocolsString=@" <".toString();
		for (i=0; i<*protocolsCount; i++){
			if (class_conformsToProtocol(classname,protocolArray[i])){
				comma=@"".toString();
				if (i<*protocolsCount-1){
					comma=@", ".toString();
				}
				protocolsString=protocolsString.toString()+protocol_getName(protocolArray[i]).toString()+comma;
			}
		}
		protocolsString=protocolsString+@">".toString();
	}
	free(protocolArray);
	if (classname.superclass!=nil && classname.superclass!="nil"){
		interfaceString = [NSString stringWithString:@"\n@interface "+classname.toString()+" : "+classname.superclass.toString()].toString() + protocolsString.toString();
	}
	else{
		interfaceString = [NSString stringWithString:@"\n@interface "+classname.toString()].toString() + protocolsString.toString();
	}
	

	while (classname!=NSObject && (classname.superclass!="nil" && classname.superclass!=NSObject) ) {

	
	// Get Ivars
	classIvarCount=new int;
	superclassIvarCount=new int;
	list=class_copyIvarList(classname,classIvarCount);
	superlist=class_copyIvarList(superclass,superclassIvarCount);
	superClassIvars=[NSMutableArray array];
	for (i=0; i<*superclassIvarCount;i++){
		if (ivar_getName(superlist[i])){
			[superClassIvars addObject:ivar_getName(superlist[i])];
		}
	
	}
	free(superlist);

	for (i=0; i<*classIvarCount;i++){
		classIvar=ivar_getName(list[i]);
		appendString="";
		if (classIvar && ![superClassIvars containsObject:classIvar]){
			ivarType=ivar_getTypeEncoding(list[i]).toString();
			ivar=constructTypeAndName([NSString stringWithString:ivarType],[NSString stringWithString:ivar_getName(list[i])],1);
			newString="\n\t"+ivar.toString()+"; "; 
			if (![ivarsString containsSubstring:newString]){
				ivarsString=ivarsString.toString()+newString.toString();
			}
		}
	
	}
	free(list);

	// Get Properties
	propertiesCount=new int;
	propertyList=class_copyPropertyList(classname,propertiesCount);
	for (i=0; i<*propertiesCount; i++){
		
		propname=property_getName(propertyList[i]);
		attrs=property_getAttributes(propertyList[i]);
		newString=propertyLineGenerator(attrs,propname).toString();
		if (![propertiesString containsSubstring:newString]){
			propertiesString=propertiesString.toString()+newString.toString();
		}
	}
	free(propertyList);

	// Get Methods
	
	methodsCount=new int;
	classMethodsCount=new int;
	classMethodList=class_copyMethodList(object_getClass(classname),classMethodsCount);
	methodList=class_copyMethodList(classname,methodsCount);
	classMethodsString=classMethodsString.toString()+methodLinesGenerator(classMethodList,classMethodsCount,1).toString();
	methodsString=methodsString.toString()+methodLinesGenerator(methodList,methodsCount,0).toString();
	free(methodList);
	free(classMethodList);
	
	if (!alsoDumpSuperclasses)
		break;
	classname=classname.superclass ? classname.superclass : NSObject;
	
	}

	
	classString= classString.toString()+structsString.toString()+interfaceString.toString();
	classString = classString.toString()+" {"+ivarsString.toString()+"\n}\n"+propertiesString.toString()+classMethodsString.toString()+methodsString.toString();  
	classString = classString.toString()+"@end";
		
	
	if (typeof(outputdir) == 'undefined'){
		outputdir = "/tmp";
	}
	
	if (typeof(alsoDumpSuperclasses) == 'string'){
		outputdir=alsoDumpSuperclasses;
	}
	
	isDir= new boolean;
	dirExists=[[NSFileManager defaultManager ] fileExistsAtPath:outputdir isDirectory: isDir] ;
	if (!dirExists || !isDir){
		createDirSucceeded = [[NSFileManager defaultManager ] createDirectoryAtPath:outputdir attributes: nil];
	}
	
	outputdir=outputdir.toString()+"/";
	
	if (![NSFileManager.defaultManager fileExistsAtPath:outputdir]){
		try{
			[NSFileManager.defaultManager createDirectoryAtPath:outputdir withIntermediateDirectories:YES attributes:nil error:nil];
		}catch(e){}
	}
	
	classString = [NSString stringWithString:classString ]; 
	if ([classString writeToFile:outputdir.toString()+startingClassname.toString()+".h" atomically:YES]){
	 
		return "Wrote file to "+outputdir.toString()+startingClassname.toString()+".h"+allProtocols.toString();
	}
	else {
		NSSearchPathForDirectoriesInDomains=new Functor(dlsym(RTLD_DEFAULT,"NSSearchPathForDirectoriesInDomains"),"@ccc");
		writeableDir=NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
		writeableDir=writeableDir[0];
		return "Failed to write to "+outputdir.toString()+startingClassname.toString()+".h - Check file path and permissions? Suggested writeable directory: "+writeableDir.toString();
	}
}




function mweak_loadwdc_class(){

	@implementation WCDBundleDumper : NSObject {}
	+(id)dumpBundle:(id)infoDictionary{
	var bundle=[infoDictionary objectForKey:@"bundle"];
	var outputdir=[infoDictionary objectForKey:@"outputdir"];


	for (d = 0; d<[ObjectiveC.classes allKeys].length; d++) {
		name=[ObjectiveC.classes allKeys][d].toString();
		if ([[NSBundle bundleForClass:objc_getClass(name.toString())] isEqual:bundle]){
			try {
				weak_classdump(objc_getClass(objc_getClass(name.toString())), false, outputdir);
			} 
			catch (e) {
			}
		}
	}
	if (typeof(__AudioServicesPlaySystemSound)=="undefined"){
	 	 dlopen("/System/Library/Frameworks/AudioToolbox.framework/AudioToolbox",RTLD_LAZY);
		__AudioServicesPlaySystemSound=new Functor(dlsym(-2,"AudioServicesPlaySystemSound"),"vi");
	}
	__AudioServicesPlaySystemSound(1005); // comment out to not produce any sound on finish
	//NSLog(@"weak_classdump: Finished dumping bundle %@. Check output dir %@",bundle,outputdir);
	
	}                                                    
	@end

}

function weak_classdump_bundle(bundle, outputdir) {

	if (typeof(bundle)=="undefined"){
		bundle=[NSBundle mainBundle];
	}
	if (![bundle isLoaded]){
		//NSLog(@"weak_classdump: Bundle %@ is not loaded,attempting to load it",bundle);
		[bundle load];
	}
	if (typeof(outputdir)=="undefined"){
		outputdir="/tmp/";
	}
	

	var infoDict=[NSMutableDictionary dictionary];
	[ infoDict setObject:bundle forKey:@"bundle"];
	[ infoDict setObject:outputdir forKey:@"outputdir"];
	
	try {	
		[WCDBundleDumper class];
	} catch (e){
		mweak_loadwdc_class();
	}  
	
	[objc_getClass("WCDBundleDumper") performSelectorInBackground:@selector(dumpBundle:) withObject:infoDict ];
	return "Dumping bundle... Will play alert sound when done. Check output directory for changes";

}
	if (! [NSString instancesRespondToSelector:@selector(containsSubstring:)]){
		@implementation NSString (lim)
		-(BOOL)containsSubstring:(NSString*)string{
			return [self rangeOfString:string].location!=NSNotFound;
		}
		@end

	}
	
	if ( ! [NSString instancesRespondToSelector:@selector(stringByRemovingCharactersFromSet:)] ){
			
			
			
			
			@implementation NSString (weakclassdump_compatibility)
			- (void)removeCharactersInSet:(id)set{
				
		    length = [this length];
			matchRange = [this rangeOfCharacterFromSet:set options:2 range:[0, length]];
			while(matchRange.length > 0){
				replaceRange = matchRange;
				searchRange=[0,0];
				searchRange.location = replaceRange.location + replaceRange.length;
				searchRange.length = length - searchRange.location;
				for(;;){
					matchRange = [this rangeOfCharacterFromSet:set options:2 range:searchRange];
					if((matchRange.length == 0) || (matchRange.location != searchRange.location))
						break;
					replaceRange.length += matchRange.length;
					searchRange.length -= matchRange.length;
					searchRange.location += matchRange.length;
				}
				[this deleteCharactersInRange:replaceRange];
				matchRange.location -= replaceRange.length;
				length -= replaceRange.length;
				}
			}
			

			- (id)stringByRemovingCharactersFromSet:(id)set{
				
				if([this rangeOfCharacterFromSet:set options:2].length == 0)
					return this;
				temp = [[this mutableCopyWithZone:[this zone]] autorelease];
				[temp removeCharactersInSet:set];
				temp=[temp stringByReplacingOccurrencesOfString: @"\"" withString: @""];
				return temp;
			}
			
			@end

	}
	
	if ( ! [NSString instancesRespondToSelector:@selector(stringByRemovingWhitespace)] ){
	
		@implementation NSString (weakclassdump_compatibility)
		-(id)stringByRemovingWhitespace{
			 return [this stringByRemovingCharactersFromSet:[NSCharacterSet whitespaceCharacterSet]];
		}
		@end
	}
	
 

// Usage example : weak_classdump(SBAwayController);
// (will write to default path "/tmp/SBAwayController.h"
// example 2: weak_classdump(UIApplication,"/var/mobile/");
// will write to "/var/mobile/UIApplication.h"
// example 3: weak_classdump_bundle([NSBundle bundleWithPath:"/System/Library/Frameworks/iAd.framework"]);
// will dump all classes in the defined bundle to default dir "/tmp" 
// example 4: weak_classdump_bundle([NSBundle bundleWithPath:"/System/Library/Frameworks/iAd.framework"],"/tmp/iAD.framework/Headers/");
// will dump all classes in the defined bundle to "/tmp/iAD.framework/"

	
"Added weak_classdump to \""+NSProcessInfo.processInfo .processName.toString()+"\" ("+NSProcessInfo.processInfo .processIdentifier.toString()+")";
