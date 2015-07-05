/*
	node-chrome-pak
	Written by Hwang, C. W. ( hikipro95(at)gmail.com )

	This script released under MIT License.
*/

/*
	version number	 = 0x00 ~ 0x03
	resource count	 = 0x04 ~ 0x07
	encoding		   = 0x08
	
	resource info :
		resource id	       = 2 bytes
		offset of resource = 4 bytes
*/

var fs = require('fs'),
	path = require('path');

var help_msg =
		"Usage: " + process.argv[0] + " " + path.basename(process.argv[1]) + " pack   [source directory] [.pak file path]\n" +
		"       " + process.argv[0] + " " + path.basename(process.argv[1]) + " unpack [.pak file path] [destination directory]\n" +
		"       " + process.argv[0] + " " + path.basename(process.argv[1]) + " replace [.pak file path] [res id] [new file path]";

console.log(
	"node-chrome-pak\n" +
	"Written by Hwang, C. W. (hikipro95@gmail.com)\n"
);

if (!process.argv[3]) {
	console.log(help_msg);
	return;
}

if (process.argv[2] == "pack") {
	pack_proc(process.argv[3], process.argv[4]);
} else if (process.argv[2] == "unpack") {
	unpack_proc(process.argv[3], process.argv[4]);
} else if (process.argv[2] == "replace") {
	replace_proc(process.argv[3], process.argv[4], process.argv[5]);
} else {
	console.log(help_msg);
	return;
}

function replace_proc(pak_file_path, src_res_id, new_file_path) {
	var pak_buf = fs.readFileSync(pak_file_path);
	var pak_fd  = fs.openSync(pak_file_path, "r+");
	
	var res_count = pak_buf.readUInt32LE(0x04);
	
	var pos = 9;
	
	var res_info = [],
		src_header_idx = 0;
	
	for (var i=0; i<res_count; i++) {
		res_info.push({
			id:	 pak_buf.readUInt16LE(pos),
			offset: pak_buf.readUInt32LE(pos + 0x02)
		});
		
		if (res_info[i].id == src_res_id) {
			src_header_idx = i;
		}
		
		pos += 0x06;
	}
	
	var new_file_buf = fs.readFileSync(new_file_path);
	
	var ori_src_res_offset = res_info[src_header_idx].offset;
	var ori_src_next_res_offset = res_info[src_header_idx+1].offset;
	
	pos = 0x00;
	
	var ori_size = res_info[src_header_idx+1].offset - res_info[src_header_idx].offset;
	
	var header_buf = new Buffer(res_count * 0x06);
	for (var i=0; i<res_count; i++) {
		header_buf.writeUInt16LE(res_info[i].id, pos);
		
		if (i > src_header_idx) {
			header_buf.writeUInt32LE(res_info[i].offset + (new_file_buf.length - ori_size), pos + 0x02);
		} else {
			header_buf.writeUInt32LE(res_info[i].offset, pos + 0x02);
		}
		
		pos += 0x06;
	}
	
	var backup_buf = pak_buf.slice(ori_src_next_res_offset, pak_buf.length);
	
	fs.writeSync(pak_fd, header_buf, 0, header_buf.length, 0x09);
	fs.writeSync(pak_fd, new_file_buf, 0, new_file_buf.length, ori_src_res_offset);
	fs.writeSync(pak_fd, backup_buf, 0, backup_buf.length, ori_src_res_offset + new_file_buf.length);
}

function pack_proc(src_dir, pack_dst_path) {
	var dst_path = (pack_dst_path ? pack_dst_path : __dirname + "/packed.pak");
	
	var pak_fd = fs.openSync(dst_path, "w+");
	
	var item_list = fs.readdirSync(src_dir);
	
	var ver_number_buf = new Buffer(0x04);
	ver_number_buf.writeUInt32LE(0x04, 0);
	
	var res_count_buf = new Buffer(0x04);
	res_count_buf.writeUInt32LE(item_list.length, 0x00);
	
	var encoding_buf = new Buffer(0x01);
	encoding_buf[0] = 0x01;
	
	fs.writeSync(pak_fd, ver_number_buf, 0, 4, 0x00);
	fs.writeSync(pak_fd, res_count_buf, 0, 4, 0x04);
	fs.writeSync(pak_fd, encoding_buf, 0, 1, 0x08);
	
	var pos = 0x09, offset_tmp = 0x09 + (item_list.length * 0x06);
	
	for (var i=0; i<item_list.length; i++) {
		var id = parseInt(item_list[i]),
			id_buf = new Buffer(2);
		
		id_buf.writeUInt16LE(id, 0x00);
		
		var size = fs.statSync(src_dir + "/" + item_list[i]).size,
			offset_buf = new Buffer(4);
		
		offset_buf.writeUInt32LE(offset_tmp, 0x00);
		offset_tmp += size;
		
		fs.writeSync(pak_fd, id_buf, 0, 2, pos);
		fs.writeSync(pak_fd, offset_buf, 0, 4, pos + 0x02);
		
		pos += 0x06;
	}
	
	for (var i=0; i<item_list.length; i++) {
		var file_buf = fs.readFileSync(src_dir + "/" + item_list[i]);
		
		fs.writeSync(pak_fd, file_buf, 0, file_buf.length, pos);
		pos += file_buf.length;
	}
	
	fs.closeSync(pak_fd);
}


function unpack_proc(pak_file_path, extract_dst_dir) {
	var pak_buf = fs.readFileSync(pak_file_path);

	var dst_dir = (extract_dst_dir ? extract_dst_dir : __dirname + "/extracted/");
	
	var ver_number = pak_buf.readUInt32LE(0x00),
		res_count  = pak_buf.readUInt32LE(0x04),
		encoding   = pak_buf.readUInt8(0x08);
	
	var pos = 0x09;
	
	var res_info = [];
	
	for (var i=0; i<res_count; i++) {
		res_info.push({
			id:     pak_buf.readUInt16LE(pos),
			offset: pak_buf.readUInt32LE(pos + 0x02)
		});
		
		pos += 0x06;
	}
	
	console.log("file count = " + res_count);
	console.log("unpacking at " + dst_dir);
	
	for (var i=0; i<res_count; i++) {
		var size = 0;
		
		if (i != res_count-1) {
			size = res_info[i+1].offset - res_info[i].offset;
		} else {
			size = pak_buf.length - res_info[i].offset;
		}
		
		var res_file_name = res_info[i].id.toString();
		
		console.log("name: " + res_file_name + ", offset: 0x" + res_info[i].offset.toString(16) + ", size: 0x" + size.toString(16));
		
		var res_buf = pak_buf.slice(res_info[i].offset, res_info[i].offset + size);
		
		if (size > 0x08) {
			if (res_buf.readUInt32BE(0x00) == 0x89504E47) { // ‰PNG
				res_file_name += ".png";
			}
		}
		
		if (!fs.existsSync(dst_dir)) { fs.mkdirSync(dst_dir); }
		
		fs.writeFileSync(dst_dir + res_file_name, res_buf);
	}
	
	console.log("unpack process complete!");
}
