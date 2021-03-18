<html>
<head>
<meta name="viewport" content="width=device-width">
<link rel="shortcut icon" type="image/x-icon" href="/cj/favicon.ico" />
<title>B站动态抽奖工具 Bili.fan</title>
</head>
<body>
<?php
/* <b>已开始筛选，耗时约一分钟，请耐心等待！</b> */
error_reporting(E_ALL^E_NOTICE);
if(strpos($_REQUEST['cookie'],'rpdid') !== false){ 
//echo '请去除cookie中的 "rpdid" 字段后再提交！'; 
$str=$_REQUEST['cookie'];
$cookie=str_replace('|','',$str);
}else{
$cookie=$_REQUEST['cookie'];
}
header("Content-type:text/html; charset=utf-8");
$cmd='py Raffle.py '. $_REQUEST['type'] .' '. $_REQUEST['dyid'] .' '. $_REQUEST['hjnum'] .' '. $cookie;
while (@ ob_end_flush()); // end all output buffers if any
set_time_limit(300);
$proc = popen($cmd, 'r');
echo '<pre>';
while (!feof($proc))
{
	    $str=fread($proc, 4096);
		$encode = mb_detect_encoding($str, array("ASCII",'UTF-8',"GB2312","GBK",'BIG5'));
        $str_encode = mb_convert_encoding($str, 'UTF-8', $encode);
        echo $str_encode;
		    @ flush();
}
echo '</pre>';
?>
</body>