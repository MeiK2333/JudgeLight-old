<?php
    header('Content-type: application/json'); //修改header以返回JSON类型数据

    $arr = array();
    $statu = array("statu" => false);

    if ($_SERVER["REMOTE_ADDR"] != '127.0.0.1') {
        /* 限制外部访问 */
        $statu['msg'] = "Only use 127.0.0.1 to access";
        echo json_encode($statu);
        return;
    }

    /* 依次获取必须的参数 */
    if ($_POST['id']) {
        $arr['id'] = $_POST['id'];
    } else {
        $statu['msg'] = "Must provide id";
        echo json_encode($statu);
        return;
    }
    $pid = $_POST['pid'];
    if ($_POST['pid']) {
        $arr['pid'] = $_POST['pid'];
    } else {
        $statu['msg'] = "Must provide pid";
        echo json_encode($statu);
        return;
    }
    if ($_POST['language']) {
        $arr['language'] = $_POST['language'];
    } else {
        $statu['msg'] = "Must provide language";
        echo json_encode($statu);
        return;
    }
    if (is_numeric($_POST['time_limit'])) {
        $arr['time_limit'] = (int)$_POST['time_limit'];
    } else {
        $statu['msg'] = "Must provide time_limit";
        echo json_encode($statu);
        return;
    }
    if (is_numeric($_POST['memory_limit'])) {
        $arr['memory_limit'] = (int)$_POST['memory_limit'];
    } else {
        $statu['msg'] = "Must provide memory_limit";
        echo json_encode($statu);
        return;
    }
    if ($_POST['special_judge'] == 'yes') {
            $arr['special_judge'] = true;
    } else {
            $arr['special_judge'] = false;
    }
    if ($_POST['all_judge'] == 'yes') {
        $arr['all_judge'] = true;
    } else {
        $arr['all_judge'] = false;
    }
    if ($_POST['code']) {
        $arr['code'] = $_POST['code'];
    } else {
        $statu['msg'] = "Must provide code";
        echo json_encode($statu);
        return;
    }
    
    $redis = new Redis();
    $redis->connect('127.0.0.1', 6379);
    $redis->lpush("judge_list", json_encode($arr)); //加入redis评测队列中
    $arr['result'] = "submit";
    $arr['prompt'] = "";
    $redis->hset("judge_result", $arr['id'], json_encode($arr)); //以id为键加入redis中,保证id必须唯一，id是查询结果的唯一凭证
    $statu['statu'] = true;
    echo json_encode($statu);
?>
