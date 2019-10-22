resource "random_string" "hello" {
  length = 16
}

resource "local_file" "hello" {
  filename = "${path.module}/hello.txt"
  content  = "${random_string.hello.result}"
}

resource "random_string" "many" {
  count  = 3
  length = 20
}

resource "local_file" "many" {
  count    = 3
  filename = "${path.module}/many.${count.index}.txt"
  content  = "${element(random_string.many.*.result, count.index)}"
}

output "content" {
  value = "${random_string.hello.result}"
}
