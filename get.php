<?php
    header('Content-type: application/json');
    $id = $_GET['id'];
    $statu = array("statu" => false);
    if ($id) {
        $redis = new Redis();
        $redis->connect('127.0.0.1', 6379);
        $result = $redis->hget("judge_result", $id);
        if ($result) {
            echo $result;
            return;
        } else {
            $statu['msg'] = "Not found";
            echo json_encode($statu);
            return;
        }
    } else {
        $statu['msg'] = "Must provide id";
        echo json_encode($statu);
        return;
    }
?>